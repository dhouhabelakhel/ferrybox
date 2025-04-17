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
import os
# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ferry_app.settings") 

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

        # Conversion de memoryview en bytes
        if isinstance(binary_data, memoryview):
            binary_data = bytes(binary_data)

        # Lecture du fichier CSV depuis les données binaires
        csv_content = binary_data.decode('ISO-8859-1')
        df = pd.read_csv(StringIO(csv_content), encoding='ISO-8859-1', skiprows=1)

        if not {'Date', 'Time', 'Latitude', 'Longitude'}.issubset(df.columns):
            logger.warning(f"Colonnes nécessaires manquantes dans {libelle}")
            return

        metadata = extract_metadata(df, libelle, binary_data)  # Passer binary_data ici
        if metadata and not Metadata.objects.filter(Name=metadata["Name"]).exists():
            append_metadata_to_csv_in_memory(metadata)
            save_metadata_to_db(metadata)

    except Exception as e:
        logger.error(f"Erreur de traitement fichier classifié : {e}", exc_info=True)

# --- EXTRACTION DES MÉTADONNÉES ---
def extract_metadata(df, file_name, binary_data):
    try:
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
            "Size_ko": len(binary_data) // 1024,  # Taille en Ko
            "Number_of_lines": len(df)
        }

    except Exception as e:
        logger.error(f"Erreur extraction métadonnées : {e}", exc_info=True)
        return None

# --- SAUVEGARDE EN FICHIER CSV LOCAL ---
def append_metadata_to_csv_in_memory(data):
    try:
        # Charger les métadonnées existantes depuis la base de données ou créer un nouveau DataFrame
        existing_metadata = get_existing_metadata_from_db()
        df_existing = pd.DataFrame(existing_metadata)

        df_new = pd.DataFrame([data])
        if not df_existing.empty:
            if data["Name"] not in df_existing["Name"].values:
                df_result = pd.concat([df_existing, df_new], ignore_index=True)
                df_result.sort_values("Path_Reference", inplace=True)
        else:
            df_result = df_new

        # Sauvegarder en mémoire
        csv_buffer = StringIO()
        df_result.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()

        # Sauvegarder dans la base de données
        save_metadata_csv_to_db(csv_content)

        logger.info("Métadonnées ajoutées en mémoire et sauvegardées dans la base de données.")

    except Exception as e:
        logger.error(f"Erreur lors de l'ajout aux métadonnées locales : {e}", exc_info=True)

# --- RECUPERATION DES METADONNÉES EXISTANTES DEPUIS LA BASE DE DONNEES ---
def get_existing_metadata_from_db():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT fichier FROM "Ferry_plot_binary_metadata" WHERE libelle = %s
        """, ("Metadata.csv",))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            csv_content = result[0].tobytes().decode('utf-8')
            return pd.read_csv(StringIO(csv_content)).to_dict(orient='records')
        return []

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métadonnées existantes : {e}", exc_info=True)
        return []

# --- SAUVEGARDE DU FICHIER CSV EN BASE DE DONNEES ---
def save_metadata_csv_to_db(csv_content):
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Vérifie si le fichier Metadata.csv existe déjà dans la table
        cur.execute("""
            SELECT 1 FROM "Ferry_plot_binary_metadata" WHERE libelle = %s
        """, ("Metadata.csv",))
        exists = cur.fetchone()

        if exists:
            cur.execute("""
                UPDATE "Ferry_plot_binary_metadata"
                SET fichier = %s
                WHERE libelle = %s
            """, (psycopg2.Binary(csv_content.encode('utf-8')), "Metadata.csv"))
            logger.info("Fichier Metadata.csv mis à jour dans Ferry_plot_binary_metadata.")
        else:
            cur.execute("""
                INSERT INTO "Ferry_plot_binary_metadata" (libelle, fichier)
                VALUES (%s, %s)
            """, ("Metadata.csv", psycopg2.Binary(csv_content.encode('utf-8'))))
            logger.info("Fichier Metadata.csv inséré dans Ferry_plot_binary_metadata.")

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier CSV en base de données : {e}", exc_info=True)

# --- SAUVEGARDE EN BASE DJANGO ---
def save_metadata_to_db(data):
    try:
        # Sauvegarde via Django ORM
        meta = Metadata(**data)
        meta.save()
        logger.info(f"Métadonnées insérées en base : {data['Name']}")

    except Exception as e:
        logger.error(f"Erreur d’insertion en base Django : {e}", exc_info=True)