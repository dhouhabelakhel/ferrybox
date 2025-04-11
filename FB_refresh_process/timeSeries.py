import os
import json
import time
import logging
import select
import warnings
from io import StringIO

import pandas as pd
from connect import connect_db

# Configuration logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
PARAMETERS = ["Salinity_SBE45", "Temp_in_SBE38", "Oxygen", "Turbidity", "Chl_a"]
DEPART_REFERENCES = ['goulette', 'Goulette']
CELL_SIZE = 5

warnings.filterwarnings('ignore', category=FutureWarning)

def listen_for_notifications():
    conn = connect_db()
    if conn is None:
        logger.error("Connexion à la base de données échouée.")
        return

    conn.set_session(autocommit=True)

    with conn.cursor() as cur:
        try:
            cur.execute("LISTEN indexed_file;")
            logger.info("En attente de notifications sur 'indexed_file'...")

            while True:
                if select.select([conn], [], [], 60) == ([], [], []):
                    logger.info("Aucune indexed file reçue... Attente...")
                    continue

                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    if notify.channel != 'indexed_file':
                        logger.warning(f"indexed file reçue d’un autre canal : {notify.channel}")
                        continue

                    try:
                        payload = json.loads(notify.payload)
                        file_id = payload.get("id")
                        libelle = payload.get("libelle", "")
                    except Exception as e:
                        logger.error(f"Erreur parsing JSON : {e}")
                        continue

                    name, table_name = detect_transect_table(libelle)
                    if not table_name:
                        logger.warning(f"Transect inconnu pour le fichier : {libelle}")
                        continue

                    logger.info(f"indexed file reçue : {libelle} (table : {table_name})")
                    cur.execute(f"SELECT libelle, fichier FROM {table_name} WHERE id = %s", (file_id,))
                    result = cur.fetchone()

                    if not result:
                        logger.warning(f"Aucun fichier indexée trouvé pour ID {file_id}")
                        continue

                    file_libelle, file_binary = result
                    process_binary_file(file_binary, file_libelle, name)

        except Exception as e:
            logger.error(f"Erreur pendant l’écoute : {e}", exc_info=True)
            time.sleep(5)

def detect_transect_table(libelle):
    libelle_lower = libelle.lower()
    if "genova" in libelle_lower:
        return "genova", '"ferry_plot_binary_indexedgenova"'
    elif "marseille" in libelle_lower:
        return "marseille", '"ferry_plot_binary_indexedmarseille"'
    return None, None

def process_binary_file(file_binary, file_name, transect_name):
    try:
        df = try_read_binary_to_df(file_binary, file_name)
        if df is None or "Cumul_Distance" not in df.columns:
            logger.error(f"Fichier invalide ou 'Cumul_Distance' manquant : {file_name}")
            return

        total_distance = df["Cumul_Distance"].iloc[-1]
        file_date = extract_date(file_name)
        depart = extract_depart(file_name)

        for param in PARAMETERS:
            if param not in df.columns:
                logger.warning(f"{param} manquant dans {file_name}")
                continue

            series = compute_parameter_series(df, param, total_distance, depart)
            FIXED_SIZE = 900
            series += [float('nan')] * (FIXED_SIZE - len(series))
            series = series[:FIXED_SIZE]

            columns = ["Date"] + [f"C_{i}" for i in range(1, FIXED_SIZE + 1)] + ["Parameter", "Transect"]
            row = [file_date] + series + [param, transect_name]
            df_series = pd.DataFrame([row], columns=columns)

            save_time_series(df_series, transect_name, param, file_date)

    except Exception as e:
        logger.error(f"Erreur dans process_binary_file : {e}", exc_info=True)

def try_read_binary_to_df(file_binary, file_name):
    try:
        return pd.read_csv(StringIO(file_binary.decode('utf-8')), delimiter=',', encoding='unicode_escape')
    except Exception:
        return None

def extract_date(file_name):
    try:
        parts = file_name.split('_')
        return parts[1] if len(parts) > 1 else time.strftime("%Y%m%d")
    except Exception:
        logger.warning("Date non extraite, fallback sur aujourd'hui")
        return time.strftime("%Y%m%d")

def extract_depart(file_name):
    try:
        if '_to_' in file_name:
            return file_name.split('_to_')[0].split('_')[-1]
        for part in file_name.split('_'):
            if part.lower() in DEPART_REFERENCES:
                return part
        logger.warning(f"Départ non trouvé dans {file_name}")
    except Exception:
        pass
    return "unknown"

def compute_parameter_series(df, param, total_distance, depart):
    series = []
    try:
        forward = depart.lower() in [d.lower() for d in DEPART_REFERENCES]
        range_values = range(0, int(total_distance), CELL_SIZE) if forward else range(int(total_distance), 0, -CELL_SIZE)

        for x in range_values:
            if forward:
                data = df[(df["Cumul_Distance"] < x) & (df["Cumul_Distance"] > x - CELL_SIZE)][param]
            else:
                data = df[(df["Cumul_Distance"] > x) & (df["Cumul_Distance"] < x + CELL_SIZE)][param]
            series.append(data.mean() if not data.empty else float('nan'))
    except Exception as e:
        logger.error(f"Erreur dans compute_parameter_series pour {param} : {e}")
    return series

def save_time_series(new_data, transect, parameter, date):
    libelle = f"{transect}_{parameter}.csv"

    try:
        conn = connect_db()
        if conn is None:
            logger.error(f"Connexion échouée pour {libelle}")
            return

        table_name = os.path.splitext(libelle)[0].lower().replace('-', '_').replace(' ', '_')

        with conn.cursor() as cur:
            cur.execute(f'''
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    id SERIAL PRIMARY KEY,
                    libelle TEXT UNIQUE,
                    fichier BYTEA
                );
            ''')

            cur.execute(f'SELECT fichier FROM "{table_name}" WHERE libelle = %s;', (libelle,))
            result = cur.fetchone()

            if result:
                try:
                    old_csv_binary = result[0]
                    old_df = pd.read_csv(StringIO(old_csv_binary.decode('utf-8')))
                    if date in old_df["Date"].values:
                        logger.info(f"Date déjà existante pour {parameter} : {date}")
                        return
                    combined_df = pd.concat([old_df, new_data], ignore_index=True)
                    combined_df.sort_values("Date", inplace=True)
                except Exception as e:
                    logger.warning(f"Erreur lecture ancienne version de {libelle} : {e}")
                    combined_df = new_data
            else:
                combined_df = new_data

            csv_buffer = StringIO()
            combined_df.to_csv(csv_buffer, index=False)
            binary_csv = csv_buffer.getvalue().encode('utf-8')

            if result:
                cur.execute(f'''
                    UPDATE "{table_name}"
                    SET fichier = %s
                    WHERE libelle = %s;
                ''', (binary_csv, libelle))
                logger.info(f"Mise à jour : {libelle} dans {table_name}")
            else:
                cur.execute(f'''
                    INSERT INTO "{table_name}" (libelle, fichier)
                    VALUES (%s, %s);
                ''', (libelle, binary_csv))
                logger.info(f"Insertion : {libelle} dans {table_name}")

            conn.commit()

    except Exception as e:
        logger.error(f"Erreur durant save_time_series pour {libelle} : {e}", exc_info=True)
    finally:
        if conn:
            conn.close()


