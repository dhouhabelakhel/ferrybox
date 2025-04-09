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

# Dossiers
DIR_PATH = 'C:/FerryBox/Processed_Files/'
TIME_SERIES_PATH = 'C:/FerryBox/time_series/'

for path in [DIR_PATH, TIME_SERIES_PATH]:
    os.makedirs(path, exist_ok=True)
    logger.info(f"Répertoire vérifié : {path}")

warnings.filterwarnings('ignore', category=FutureWarning)

# Constantes
PARAMETERS = ["Salinity_SBE45", "Temp_in_SBE38", "Oxygen", "Turbidity", "Chl_a"]
DEPART_REFERENCES = ['goulette', 'Goulette']
CELL_SIZE = 5

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
                    file_path = os.path.join(DIR_PATH, file_libelle)
                    with open(file_path, 'wb') as f:
                        f.write(file_binary)
                    logger.info(f"Fichier indexée enregistré : {file_path}")

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

            # Fixer le nombre de colonnes à 178
            FIXED_SIZE = 900
            series += [float('nan')] * (FIXED_SIZE - len(series))  # Compléter avec NaN si nécessaire
            series = series[:FIXED_SIZE]  # Tronquer si dépasse

            # Créer le DataFrame avec les colonnes C_1 à C_178
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
        temp_path = os.path.join(DIR_PATH, f"temp_{file_name}")
        with open(temp_path, 'wb') as f:
            f.write(file_binary)
        try:
            return pd.read_csv(temp_path, delimiter=',', encoding='unicode_escape')
        finally:
            os.remove(temp_path)

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
    output_path = os.path.join(TIME_SERIES_PATH, f"{transect}_{parameter}.csv")
    libelle = os.path.basename(output_path)

    try:
        if os.path.exists(output_path):
            df_existing = pd.read_csv(output_path)
            if date not in df_existing["Date"].values:
                result = pd.concat([df_existing, new_data], ignore_index=True)
                result.sort_values("Date", inplace=True)
                result.to_csv(output_path, index=False)
                logger.info(f"Données mises à jour : {output_path}")
            else:
                logger.info(f"Date déjà existante pour {parameter} : {date}")
                return
        else:
            new_data.to_csv(output_path, index=False)
            logger.info(f"Fichier créé : {output_path}")

        insert_csv_to_db(output_path, libelle)

    except Exception as e:
        logger.error(f"Erreur en sauvegardant la série temporelle : {e}")

def insert_csv_to_db(csv_path, libelle):
    conn = connect_db()
    if conn is None:
        logger.error(f"Connexion à la BD échouée pour {libelle}")
        return

    try:
        with open(csv_path, 'rb') as f:
            binary_data = f.read()

        table_name = os.path.splitext(libelle)[0].lower().replace('-', '_').replace(' ', '_')

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
                ''', (binary_data, libelle))
                logger.info(f"Fichier '{libelle}' mis à jour dans la table {table_name}.")
            else:
                cur.execute(f'''
                    INSERT INTO "{table_name}" (libelle, fichier)
                    VALUES (%s, %s);
                ''', (libelle, binary_data))
                logger.info(f"Fichier '{libelle}' inséré dans la table {table_name}.")

            conn.commit()

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion ou mise à jour de {csv_path} dans {table_name} : {e}")
    finally:
        conn.close()