import json
import time
import logging
import select
import warnings
from io import StringIO, BytesIO
import os
import psycopg2
import pandas as pd
from connect import connect_db

# Configuration logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore', category=FutureWarning)

# Constantes
PARAMETERS = ["Salinity_SBE45", "Temp_in_SBE38", "Oxygen", "Turbidity", "Chl_a"]
DEPART_REFERENCES = ['goulette', 'Goulette']
CELL_SIZE = 5

def listen_for_notifications():
    conn = connect_db()
    if conn is None:
        logger.error("Database connection failed.")
        return

    conn.set_session(autocommit=True)

    with conn.cursor() as cur:
        try:
            cur.execute("LISTEN indexed_file;")
            logger.info("Waiting for notifications on 'indexed_file'...")

            while True:
                if select.select([conn], [], [], 60) == ([], [], []):
                    logger.info("No indexed file received... Waiting...")
                    continue

                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    if notify.channel != 'indexed_file':
                        logger.warning(f"indexed file received from another channel: {notify.channel}")
                        continue

                    try:
                        payload = json.loads(notify.payload)
                        file_id = payload.get("id")
                        libelle = payload.get("libelle", "")
                    except Exception as e:
                        logger.error(f"JSON parsing error: {e}")
                        continue

                    name, table_name = detect_transect_table(libelle)
                    if not table_name:
                        logger.warning(f"Unknown transect for file: {libelle}")
                        continue

                    logger.info(f"indexed file received: {libelle} (table : {table_name})")
                    cur.execute(f"SELECT libelle, fichier FROM {table_name} WHERE id = %s", (file_id,))
                    result = cur.fetchone()

                    if not result:
                        logger.warning(f"No indexed files found for ID {file_id}")
                        continue

                    file_libelle, file_binary = result
                    process_binary_file(file_binary, file_libelle, name)

        except Exception as e:
            logger.error(f"Error while listening: {e}", exc_info=True)
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
        # Conversion de memoryview en bytes
        if isinstance(file_binary, memoryview):
            file_binary = bytes(file_binary)

        df = try_read_binary_to_df(file_binary, file_name)
        if df is None or "Cumul_Distance" not in df.columns:
            return

        total_distance = df["Cumul_Distance"].iloc[-1]
        file_date = extract_date(file_name)
        depart = extract_depart(file_name)

        for param in PARAMETERS:
            if param not in df.columns:
                continue

            series = compute_parameter_series(df, param, total_distance, depart)

            # Fixer le nombre de colonnes à 900
            FIXED_SIZE = 900
            series += [float('nan')] * (FIXED_SIZE - len(series))  # Compléter avec NaN si nécessaire
            series = series[:FIXED_SIZE]  # Tronquer si dépasse

            # Créer le DataFrame avec les colonnes C_1 à C_900
            columns = ["Date"] + [f"C_{i}" for i in range(1, FIXED_SIZE + 1)] + ["Parameter", "Transect"]
            row = [file_date] + series + [param, transect_name]
            df_series = pd.DataFrame([row], columns=columns)

            save_time_series_in_memory(df_series, transect_name, param, file_date)

    except Exception as e:
        logger.error(f"Error in process_binary_file:{e}", exc_info=True)

def try_read_binary_to_df(file_binary, file_name):
    try:
        return pd.read_csv(StringIO(file_binary.decode('utf-8')), delimiter=',', encoding='unicode_escape')
    except Exception as e:
        logger.error(f"Error reading binary file: {e}")
        return None

def extract_date(file_name):
    try:
        parts = file_name.split('_')
        return parts[1] if len(parts) > 1 else time.strftime("%Y%m%d")
    except Exception:
        logger.warning("Date not extracted, fallback to today")
        return time.strftime("%Y%m%d")

def extract_depart(file_name):
    try:
        if '_to_' in file_name:
            return file_name.split('_to_')[0].split('_')[-1]
        for part in file_name.split('_'):
            if part.lower() in DEPART_REFERENCES:
                return part
        logger.warning(f"Departure not found in{file_name}")
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
        logger.error(f"Error in compute_parameter_series for {param} : {e}")
    return series

def save_time_series_in_memory(new_data, transect, parameter, date):
    table_name = f"{transect}_{parameter}".lower().replace('-', '_').replace(' ', '_')

    try:
        # Récupérer les données existantes depuis la base de données
        existing_data = get_existing_time_series_from_db(table_name)
        if existing_data:
            df_existing = pd.DataFrame(existing_data)
            if date not in df_existing["Date"].values:
                result = pd.concat([df_existing, new_data], ignore_index=True)
                result.sort_values("Date", inplace=True)
            else:
                logger.info(f"Date already exists for {parameter} : {date}")
                return
        else:
            result = new_data

        # Sauvegarder le résultat en mémoire
        buffer = StringIO()
        result.to_csv(buffer, index=False)
        csv_content = buffer.getvalue().encode('utf-8')

        # Insérer ou mettre à jour les données dans la base de données
        insert_or_update_csv_in_db(table_name, f"{transect}_{parameter}.csv", csv_content)

    except Exception as e:
        logger.error(f"Error saving time series: {e}")

def get_existing_time_series_from_db(table_name):
    conn = connect_db()
    if conn is None:
        logger.error("Unable to connect to the database.")
        return []

    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT fichier FROM "{table_name}"
                WHERE libelle = %s
            """, (f"{table_name}.csv",))
            result = cur.fetchone()
            if result:
                csv_content = result[0].tobytes().decode('utf-8')
                return pd.read_csv(StringIO(csv_content)).to_dict(orient='records')
            return []

    except Exception as e:
        logger.error(f"Error retrieving existing data: {e}")
        return []

def insert_or_update_csv_in_db(table_name, libelle, csv_content):
    conn = connect_db()
    if conn is None:
        logger.error(f"Connexion à la BD échouée pour {libelle}")
        return

    try:
        with conn.cursor() as cur:
            cur.execute(f'''
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    id SERIAL PRIMARY KEY,
                    libelle TEXT UNIQUE,
                    fichier BYTEA
                );
            ''')

            cur.execute(f'SELECT id FROM "{table_name}" WHERE libelle = %s;', (libelle,))
            result = cur.fetchone()

            if result:
                cur.execute(f'''
                    UPDATE "{table_name}"
                    SET fichier = %s
                    WHERE libelle = %s;
                ''', (psycopg2.Binary(csv_content), libelle))
                logger.info(f"File '{libelle}' updated in table {table_name}.")
            else:
                cur.execute(f'''
                    INSERT INTO "{table_name}" (libelle, fichier)
                    VALUES (%s, %s);
                ''', (libelle, psycopg2.Binary(csv_content)))
                logger.info(f"File '{libelle}' inserted into the table {table_name}.")

            conn.commit()

    except Exception as e:
        logger.error(f"Error inserting or updating {libelle} in {table_name} : {e}")
    finally:
        conn.close()