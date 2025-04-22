import imaplib
import email
import psycopg2
import unicodedata
from datetime import datetime
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import zipfile
import io
import logging
# Configuration IMAP Gmail
EMAIL_USER = settings.EMAIL_HOST_USER
EMAIL_PASS = settings.EMAIL_HOST_PASSWORD
SENDER_EMAIL = "ferryboxinstm@gmail.com"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connexion à la base de données PostgreSQL
def connect_db():
    db_config = {
        'dbname': settings.DATABASES['default']['NAME'],
        'user': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD'],
        'host': settings.DATABASES['default']['HOST'],
        'port': settings.DATABASES['default']['PORT'],
    }
    try:
        conn = psycopg2.connect(**db_config)
        print("Connexion à PostgreSQL réussie")
        return conn
    except Exception as e:
        print(f"Erreur de connexion à PostgreSQL : {e}")
        return None

# Enregistrement du fichier dans la base de données + notification
def save_file_to_db(file_name, file_data):
    connection = None
    cursor = None
    try:
        connection = connect_db()
        if connection is None:
            return
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM ferry_plot_binary_email WHERE file_name = %s", (file_name,))
        if cursor.fetchone():
            logger.error(f"The file {file_name} already exists in the database. Ignore the insert.")
            return

        query = """
            INSERT INTO ferry_plot_binary_email (file_name, file_data, received_at)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (file_name, psycopg2.Binary(file_data), datetime.now()))
        connection.commit()
        logger.info(f"File {file_name} saved in Data Base.")

        # Envoi de notification en temps réel via Django Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",  # nom du groupe
            {
                "type": "send_notification",  # nom du handler dans consumer.py
                "message": f"New file received: {file_name}",
            },
        )
    except psycopg2.Error as err:
        logger.error(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Traitement des nouveaux emails
def process_new_emails():
    logger.info("Running process_new_emails...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mailboxes = ["INBOX", "[Gmail]/Spam"]

        for mailbox in mailboxes:
            logger.debug(f"Checking in {mailbox}...")
            mail.select(mailbox)
            result, data = mail.search(None, f'(UNSEEN FROM "{SENDER_EMAIL}")')
            email_ids = data[0].split() if data[0] else []

            if not email_ids:
                logger.info(f"No new emails from {SENDER_EMAIL} in {mailbox}")
                continue

            for email_id in email_ids:
                try:
                    _, msg_data = mail.fetch(email_id, "(RFC822)")
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)

                    for part in email_message.walk():
                        if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                            continue

                        file_name = part.get_filename()
                        if file_name:
                            file_name = email.header.decode_header(file_name)[0][0]
                            if isinstance(file_name, bytes):
                                file_name = file_name.decode()
                            file_name = unicodedata.normalize('NFKD', file_name)

                            file_data = part.get_payload(decode=True)
                            if file_name.endswith(".zip"):
                                handle_zip_file(file_name, file_data)
                            else:
                                save_file_to_db(file_name, file_data)
                except Exception as e:
                    logger.error(f"Error processing an email: {e}")

        mail.logout()
        logger.info("Email processing completed.")
    except Exception as e:
        logger.error(f"Erreur : {e}")

# Extraction des fichiers ZIP et traitement
def handle_zip_file(zip_file_name, zip_file_data):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_file_data), 'r') as zip_ref:
            logger.debug(f"ZIP file {zip_file_name} extract.")
            for file_name in zip_ref.namelist():
                file_data = zip_ref.read(file_name)
                save_file_to_db(file_name, file_data)
    except Exception as e:
        logger.error(f"Error handling ZIP: {e}")