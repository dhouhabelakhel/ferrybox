import os
import json
import time
import logging
import select
import warnings
from io import StringIO, BytesIO
from datetime import datetime
import pandas as pd
import geopy.distance as geo_dist
import psycopg2
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ferry_app.settings") 
django.setup()

from Ferry_plot.models import Metadata
from connect import connect_db

# --- CONFIGURATION ---
warnings.simplefilter(action='ignore', category=FutureWarning)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ÉCOUTE DES NOTIFICATIONS ---
def listen_for_notifications():
    conn = connect_db()
    if conn is None:
        logger.error("Connexion à la base de données échouée.")
        return
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    try:
        cur.execute("LISTEN classificated_files;")
        logger.info("En attente de notifications sur 'classificated_files'...")

        while True:
            if select.select([conn], [], [], 60) == ([], [], []):
                logger.info("Aucune notification reçue. Attente...")
                continue

            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                payload = json.loads(notify.payload)
                file_id = payload.get("id")
                libelle = payload.get("libelle")
                logger.info(f"Notification reçue : {libelle} (ID: {file_id})")

                table_name = None
                if "genova" in libelle.lower():
                    table_name = '"Ferry_plot_binary_classifiedgenova"'
                elif "marseille" in libelle.lower():
                    table_name = '"Ferry_plot_binary_classifiedmarseille"'

                process_classified_file(file_id, libelle, cur, table_name)

    except Exception as e:
        logger.error(f"Erreur pendant l’écoute : {e}", exc_info=True)
        time.sleep(5)

# --- TRAITEMENT DES FICHIERS CLASSIFIÉS ---
def process_classified_file(file_id, libelle, cur, table_name):
    try:
        cur.execute(f"SELECT fichier FROM {table_name} WHERE id = %s", (file_id,))
        result = cur.fetchone()
        if not result:
            logger.warning(f"Fichier ID {file_id} introuvable.")
            return

        binary_data = result[0]
        file_stream = BytesIO(binary_data)

        if not libelle.lower().endswith('.csv'):
            logger.warning("Le fichier reçu n'est pas un CSV. Abandon du traitement.")
            return

        df = pd.read_csv(file_stream, encoding='ISO-8859-1', skiprows=1)

        if not {'Date', 'Time', 'Latitude', 'Longitude'}.issubset(df.columns):
            logger.warning(f"Colonnes nécessaires manquantes dans {libelle}")
            return

        metadata = extract_metadata(df, libelle, binary_data)
        if metadata and not Metadata.objects.filter(Name=metadata["Name"]).exists():
            save_metadata_to_db(metadata)

    except Exception as e:
        logger.error(f"Erreur de traitement fichier classifié : {e}", exc_info=True)

# --- EXTRACTION DES MÉTADONNÉES ---
def extract_metadata(df, libelle, binary_data):
    try:
        file_name = os.path.basename(libelle)
        name = file_name.split(".csv")[0]
        info = name.split("_")
        ref = int(info[0])
        date_str = info[1]
        time_str = info[2]
        transect = info[3:6]
        depart, destination = transect[0], transect[2]

        sens = "Back" if "goulette" in destination.lower() else "Forth"
        season = "Summer" if date_str.split("-")[1] in ["03", "04", "05", "06", "07", "08"] else "Winter"
        year = int(date_str.split("-")[0])
        date_dt = datetime.strptime(date_str, "%Y-%m-%d")

        df["Date Time"] = pd.to_datetime(df["Date"] + " " + df["Time"])
        start_time = df["Date Time"].iloc[0]
        end_time = df["Date Time"].iloc[-1]
        duration = abs((end_time - start_time).total_seconds() / 3600)

        coords_start = (df["Latitude"].iloc[0], df["Longitude"].iloc[0])
        coords_end = (df["Latitude"].iloc[-1], df["Longitude"].iloc[-1])
        distance_km = int(geo_dist.distance(coords_start, coords_end).km)

        return {
            "Name": name,
            "sens": sens,
            "Path_Reference": ref,
            "Port_name": destination,
            "Departure": depart,
            "Destination": destination,
            "Year": year,
            "Date": date_dt,
            "Season": season,
            "Start_time": start_time.time(),
            "End_time": end_time.time(),
            "Duration_h": int(duration),
            "Distance_km": distance_km,
            "Size_ko": int(len(binary_data) / 1024),
            "Number_of_lines": len(df)
        }

    except Exception as e:
        logger.error(f"Erreur extraction métadonnées : {e}", exc_info=True)
        return None

# --- GÉNÉRATION CSV EN MÉMOIRE ---
from django.forms.models import model_to_dict

def build_metadata_csv_from_db():
    all_metadata = Metadata.objects.all().order_by("Path_Reference")
    df = pd.DataFrame([model_to_dict(meta) for meta in all_metadata])
    return df.to_csv(index=False).encode("utf-8")

# --- SAUVEGARDE EN BASE DJANGO & PG ---
def save_metadata_to_db(data):
    try:
        meta = Metadata(**data)
        meta.save()
        logger.info(f"Métadonnées insérées en base : {data['Name']}")

        csv_binary = build_metadata_csv_from_db()
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM "Ferry_plot_binary_metadata" WHERE libelle = %s
        """, ("Metadata.csv",))
        exists = cur.fetchone()

        if exists:
            cur.execute("""
                UPDATE "Ferry_plot_binary_metadata"
                SET fichier = %s
                WHERE libelle = %s
            """, (psycopg2.Binary(csv_binary), "Metadata.csv"))
            logger.info("Fichier Metadata.csv mis à jour dans Ferry_plot_binary_metadata.")
        else:
            cur.execute("""
                INSERT INTO "Ferry_plot_binary_metadata" (libelle, fichier)
                VALUES (%s, %s)
            """, ("Metadata.csv", psycopg2.Binary(csv_binary)))
            logger.info("Fichier Metadata.csv inséré dans Ferry_plot_binary_metadata.")

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        logger.error(f"Erreur d’insertion en base Django ou PostgreSQL : {e}", exc_info=True)
