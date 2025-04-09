import os
import logging
import select
import sys
import time
import csv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connect import connect_db

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMP_DIR = "C:/dsi3/stage Pfe/temp"
ERROR_DIR = "C:/dsi3/stage Pfe/errors"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)

def fetch_and_write_binary_file(file_data, file_name):
    try:
        temp_path = os.path.join(TEMP_DIR, file_name)
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(file_data)
        return temp_path
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier temporaire {file_name} : {e}")
        return None

def insert_classified_file_into_db(table_name, file_name, file_data, db_conn):
    try:
        with db_conn.cursor() as cur:
            insert_query = f"""INSERT INTO "{table_name}" (libelle, fichier) VALUES (%s, %s);"""
            cur.execute(insert_query, (file_name, file_data))
            db_conn.commit()
            logger.info(f"Fichier {file_name} inséré dans la table {table_name}.")
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion dans {table_name}: {e}")
        db_conn.rollback()

def convert_txt_to_csv(file_name, temp_path):
    try:
        output_csv_path = temp_path.replace(".txt", ".csv")
        with open(temp_path, 'r', encoding='utf-8', errors='ignore') as txt_file, open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            reader = txt_file.readlines()
            writer = csv.writer(csv_file)

            datasets_started = False
            headers_written = False
            for line in reader:
                line = line.strip()
                if line == "$DATASETS":
                    datasets_started = True
                    continue
                if datasets_started:
                    if not headers_written:
                        headers_line = next((l.strip() for l in reader if l.strip()), None)
                        if headers_line:
                            writer.writerow(headers_line.split())
                            headers_written = True
                        continue
                    if line:
                        writer.writerow(line.split())

        logger.info(f"File {file_name} successfully converted to CSV: {output_csv_path}.")
        return output_csv_path
    except Exception as e:
        logger.error(f"Error converting {file_name} to CSV: {e}")
        return None

def classify_binary_file_and_store(file_name, file_data, db_conn):
    try:
        temp_path = fetch_and_write_binary_file(file_data, file_name)
        if not temp_path:
            raise Exception(f"Impossible de traiter le fichier {file_name}. Chemin temporaire introuvable.")

        if file_name.endswith(".txt"):
            temp_csv_path = convert_txt_to_csv(file_name, temp_path)
            if not temp_csv_path:
                raise Exception(f"Conversion de {file_name} en CSV échouée.")
            temp_path = temp_csv_path  

        file_size = os.path.getsize(temp_path)

        if file_size < 200000 or file_size > 1000000:
            table_name = "ferry_plot_binary_truncated_files"
        else:
            if "genova" in file_name.lower():
                table_name = "Ferry_plot_binary_classifiedgenova"
            elif "marseille" in file_name.lower():
                table_name = "Ferry_plot_binary_classifiedmarseille"
            else:
                table_name = "Ferry_plot_binary_error_logs"

        with open(temp_path, 'rb') as binary_file:
            file_data = binary_file.read()
        insert_classified_file_into_db(table_name, file_name.replace(".txt", ".csv"), file_data, db_conn)

    except Exception as e:
        logger.error(f"Erreur lors de la classification et du stockage pour {file_name}: {e}")
        error_csv_path = os.path.join(ERROR_DIR, file_name.replace(".txt", "_error.csv"))
        with open(error_csv_path, 'w', newline='', encoding='utf-8') as error_csv:
            writer = csv.writer(error_csv)
            writer.writerow(["Fichier", "Erreur"])
            writer.writerow([file_name, str(e)])

        with open(error_csv_path, 'rb') as error_file:
            error_data = error_file.read()
        insert_classified_file_into_db("Ferry_plot_binary_error_logs", file_name.replace(".txt", "_error.csv"), error_data, db_conn)

def listen_for_notifications():
    conn = connect_db()
    if conn is None:
        logger.error("Impossible de se connecter à la base de données.")
        return

    conn.set_session(autocommit=True)
    cur = conn.cursor()

    try:
        cur.execute("LISTEN new_file;")
        logger.info("En attente de notifications sur le canal 'new_file'...")

        while True:
            if select.select([conn], [], [], 60) == ([], [], []):
                logger.info("Aucun événement reçu... Attente...")
                continue

            conn.poll()

            while conn.notifies:
                notify = conn.notifies.pop(0)

                if notify.channel != 'new_file':
                    logger.warning(f"Notification reçue d'un autre canal : {notify.channel}")
                    continue

                new_file_id = notify.payload
                logger.info(f"Notification reçue sur le canal 'new_file'. Nouveau fichier ID : {new_file_id}")
                
                cur.execute("SELECT file_name, file_data FROM ferry_plot_binary_email WHERE id = %s;", (new_file_id,))
                result = cur.fetchone()

                if result:
                    file_name, file_data = result
                    logger.info(f"email récupéré : {file_name}")
                    classify_binary_file_and_store(file_name, file_data, conn)
                else:
                    logger.warning(f"Aucun email trouvé pour l'ID : {new_file_id}")

    except Exception as e:
        logger.error(f"Erreur : {e}")
        time.sleep(5)
    finally:
        cur.close()
        conn.close()
