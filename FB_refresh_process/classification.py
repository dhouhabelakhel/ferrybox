import logging
import select
import sys
import time
import csv
import io
import os
import psycopg2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connect import connect_db

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_binary_file(file_data):
    try:
        # Retourne directement les données binaires sans écrire sur le disque
        return file_data
    except Exception as e:
        logger.error(f"Error retrieving binary data: {e}")
        return None

def insert_classified_file_into_db(table_name, file_name, file_data, db_conn):
    try:
        with db_conn.cursor() as cur:
            insert_query = f"""INSERT INTO "{table_name}" (libelle, fichier) VALUES (%s, %s);"""
            cur.execute(insert_query, (file_name, psycopg2.Binary(file_data)))
            db_conn.commit()
            logger.info(f"File {file_name} inserted into the table {table_name}.")
    except Exception as e:
        logger.error(f"Error inserting into {table_name}: {e}")
        db_conn.rollback()

def convert_txt_to_csv_in_memory(file_name, file_data):
    try:
        # Lecture du contenu du fichier texte depuis les données binaires
        text_content = file_data.decode('utf-8', errors='ignore').splitlines()

        # Préparation du contenu CSV en mémoire
        output_csv = io.StringIO()
        writer = csv.writer(output_csv)

        datasets_started = False
        headers_written = False
        for line in text_content:
            line = line.strip()
            if line == "$DATASETS":
                datasets_started = True
                continue
            if datasets_started:
                if not headers_written:
                    headers_line = next((l.strip() for l in text_content if l.strip()), None)
                    if headers_line:
                        writer.writerow(headers_line.split())
                        headers_written = True
                    continue
                if line:
                    writer.writerow(line.split())

        # Conversion du contenu CSV en données binaires
        csv_data = output_csv.getvalue().encode('utf-8')
        logger.info(f"File {file_name} convert to CSV.")
        return csv_data
    except Exception as e:
        logger.error(f"Error converting to CSV for {file_name}: {e}")
        return None

def classify_binary_file_and_store(file_name, file_data, db_conn):
    try:
        # Conversion de memoryview en bytes
        if isinstance(file_data, memoryview):
            file_data = bytes(file_data)

        # Conversion TXT → CSV si nécessaire
        if file_name.endswith(".txt"):
            file_data = convert_txt_to_csv_in_memory(file_name, file_data)
            if not file_data:
                raise Exception(f"Conversion of {file_name} to CSV failed.")
            file_name = file_name.replace(".txt", ".csv")

        # Classification en fonction de la taille ou du nom
        file_size = len(file_data)

        if file_size < 200000 or file_size > 1000000:
            table_name = "ferry_plot_binary_truncated_files"
        else:
            if "genova" in file_name.lower():
                table_name = "Ferry_plot_binary_classifiedgenova"
            elif "marseille" in file_name.lower():
                table_name = "Ferry_plot_binary_classifiedmarseille"
            else:
                table_name = "Ferry_plot_binary_error_logs"

        # Insertion dans la base de données
        insert_classified_file_into_db(table_name, file_name, file_data, db_conn)

    except Exception as e:
        logger.error(f"Error in classification and storage for {file_name}: {e}")

        # Gestion des erreurs en mémoire
        error_csv_data = io.StringIO()
        writer = csv.writer(error_csv_data)
        writer.writerow(["Fichier", "Erreur"])
        writer.writerow([file_name, str(e)])
        error_csv_binary = error_csv_data.getvalue().encode('utf-8')

        # Insertion des logs d'erreur dans la base de données
        insert_classified_file_into_db("Ferry_plot_binary_error_logs", file_name.replace(".txt", "_error.csv"), error_csv_binary, db_conn)

def listen_for_notifications():
    conn = connect_db()
    if conn is None:
        logger.error("Unable to connect to the database.")
        return

    conn.set_session(autocommit=True)
    cur = conn.cursor()

    try:
        cur.execute("LISTEN new_file;")
        logger.info("Waiting for notifications on the 'new_file' channel...")

        while True:
            if select.select([conn], [], [], 60) == ([], [], []):
                logger.info("No events received... Waiting...")
                continue

            conn.poll()

            while conn.notifies:
                notify = conn.notifies.pop(0)

                if notify.channel != 'new_file':
                    logger.warning(f"Notification received from another channel: {notify.channel}")
                    continue

                new_file_id = notify.payload
                logger.info(f"Notification received on channel 'new_file'. New file ID: {new_file_id}")
                
                cur.execute("SELECT file_name, file_data FROM ferry_plot_binary_email WHERE id = %s;", (new_file_id,))
                result = cur.fetchone()

                if result:
                    file_name, file_data = result
                    logger.info(f"Email récupéré : {file_name}")
                    classify_binary_file_and_store(file_name, file_data, conn)
                else:
                    logger.warning(f"No email found for ID: {new_file_id}")

    except Exception as e:
        logger.error(f"Erreur : {e}")
        time.sleep(5)
    finally:
        cur.close()
        conn.close()