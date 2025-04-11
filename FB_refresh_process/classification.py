import logging
import select
import sys
import time
import csv
import io
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from connect import connect_db

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Insert un fichier binaire dans la table PostgreSQL
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

# Conversion TXT vers CSV (tout en mémoire)
def convert_txt_to_csv_memory(file_name, file_data):
    try:
        # Si file_data est un memoryview, on le convertit en bytes
        if isinstance(file_data, memoryview):
            file_data = file_data.tobytes()

        # Décode les données binaires en texte
        txt_stream = io.StringIO(file_data.decode('utf-8', errors='ignore'))
        csv_stream = io.StringIO()
        writer = csv.writer(csv_stream)

        lines = txt_stream.readlines()
        datasets_started = False
        headers_written = False

        for idx, line in enumerate(lines):
            line = line.strip()
            if line == "$DATASETS":
                datasets_started = True
                continue
            if datasets_started:
                if not headers_written:
                    for l in lines[idx+1:]:
                        l = l.strip()
                        if l:
                            writer.writerow(l.split())
                            headers_written = True
                            break
                    continue
                if line:
                    writer.writerow(line.split())

        csv_bytes = csv_stream.getvalue().encode('utf-8')  # Conversion du CSV en bytes
        return csv_bytes
    except Exception as e:
        logger.error(f"Erreur conversion CSV mémoire pour {file_name} : {e}")
        return None

# Classification et insertion en mémoire
def classify_binary_file_and_store(file_name, file_data, db_conn):
    try:
        if file_name.endswith(".txt"):
            csv_data = convert_txt_to_csv_memory(file_name, file_data)
            if csv_data is None:
                raise Exception(f"Conversion CSV échouée pour {file_name}")
            file_data = csv_data
            file_name = file_name.replace(".txt", ".csv")

        file_size = len(file_data)
        if file_size < 200000 or file_size > 1000000:
            table_name = "ferry_plot_binary_truncated_files"
        else:
            lower_name = file_name.lower()
            if "genova" in lower_name:
                table_name = "Ferry_plot_binary_classifiedgenova"
            elif "marseille" in lower_name:
                table_name = "Ferry_plot_binary_classifiedmarseille"
            else:
                table_name = "Ferry_plot_binary_error_logs"

        insert_classified_file_into_db(table_name, file_name, file_data, db_conn)

    except Exception as e:
        logger.error(f"Erreur classification fichier {file_name}: {e}")
        error_stream = io.StringIO()
        writer = csv.writer(error_stream)
        writer.writerow(["Fichier", "Erreur"])
        writer.writerow([file_name, str(e)])
        error_data = error_stream.getvalue().encode('utf-8')
        error_file_name = file_name.replace(".txt", "_error.csv")
        insert_classified_file_into_db("Ferry_plot_binary_error_logs", error_file_name, error_data, db_conn)

# Écoute du canal PostgreSQL
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
                logger.info(f"Notification reçue. Nouveau fichier ID : {new_file_id}")
                
                cur.execute("SELECT file_name, file_data FROM ferry_plot_binary_email WHERE id = %s;", (new_file_id,))
                result = cur.fetchone()

                if result:
                    file_name, file_data = result
                    logger.info(f"Traitement de : {file_name}")
                    classify_binary_file_and_store(file_name, file_data, conn)
                else:
                    logger.warning(f"Aucun fichier trouvé pour l'ID : {new_file_id}")

    except Exception as e:
        logger.error(f"Erreur d'écoute : {e}")
        time.sleep(5)
    finally:
        cur.close()
        conn.close()

