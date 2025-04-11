import imaplib
import email
import psycopg2
import unicodedata
import zipfile
from io import BytesIO
from datetime import datetime
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Configuration IMAP Gmail
EMAIL_USER = settings.EMAIL_HOST_USER
EMAIL_PASS = settings.EMAIL_HOST_PASSWORD
SENDER_EMAIL = "ferryboxinstm@gmail.com"

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

# Enregistrement en base de données depuis des données binaires en mémoire
def save_file_to_db_memory(file_data, file_name):
    connection = None
    cursor = None
    try:
        connection = connect_db()
        if connection is None:
            return

        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM ferry_plot_binary_email WHERE file_name = %s", (file_name,))
        if cursor.fetchone():
            print(f"Le fichier {file_name} existe déjà dans la base de données. Ignorer l'insertion.")
            return

        query = """
            INSERT INTO ferry_plot_binary_email (file_name, file_data, received_at)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (file_name, psycopg2.Binary(file_data), datetime.now()))
        connection.commit()
        print(f"Fichier {file_name} enregistré dans PostgreSQL.")

        # Notification en temps réel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "send_notification",
                "message": f"Nouveau fichier reçu : {file_name}",
            },
        )

    except psycopg2.Error as err:
        print(f"Erreur PostgreSQL : {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Décompression et traitement des fichiers ZIP en mémoire
def unzip_and_save_memory(zip_bytes):
    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as zip_ref:
            for file_info in zip_ref.infolist():
                with zip_ref.open(file_info.filename) as extracted_file:
                    file_data = extracted_file.read()
                    file_name = unicodedata.normalize('NFKD', file_info.filename)
                    save_file_to_db_memory(file_data, file_name)
        print("ZIP traité entièrement en mémoire.")
    except Exception as e:
        print(f"Erreur lors de la gestion du ZIP en mémoire : {e}")

# Traitement des nouveaux emails
def process_new_emails():
    print("Exécution de process_new_emails...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mailboxes = ["INBOX", "[Gmail]/Spam"]

        for mailbox in mailboxes:
            print(f"Vérification dans {mailbox}...")
            mail.select(mailbox)
            result, data = mail.search(None, f'(UNSEEN FROM "{SENDER_EMAIL}")')
            email_ids = data[0].split() if data[0] else []

            if not email_ids:
                print(f"Aucun nouvel e-mail de {SENDER_EMAIL} dans {mailbox}")
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
                                unzip_and_save_memory(file_data)
                            else:
                                save_file_to_db_memory(file_data, file_name)
                except Exception as e:
                    print(f"Erreur lors du traitement d'un e-mail : {e}")

        mail.logout()
        print("Traitement des e-mails terminé.")
    except Exception as e:
        print(f"Erreur : {e}")
