import os
import zipfile
import imaplib
import email
import psycopg2
import time
from datetime import datetime
from django.conf import settings

# Configuration IMAP Gmail
EMAIL_USER = settings.EMAIL_HOST_USER
EMAIL_PASS = settings.EMAIL_HOST_PASSWORD
# Stocker les email recu de ce sender seulement
SENDER_EMAIL = "dhouhabelakhel2001@gmail.com"

# Dossier temporaire pour stocker les fichiers
DOWNLOAD_DIR = "C:/FerryBox/Mails/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Connexion à la base de données PostgreSQL
def connect_db():
    """Établit la connexion PostgreSQL en utilisant la configuration de Django."""
    db_config = {
        'dbname': settings.DATABASES['default']['NAME'],
        'user': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD'],
        'host': settings.DATABASES['default']['HOST'],
        'port': settings.DATABASES['default']['PORT'],
    }
    try:
        conn = psycopg2.connect(**db_config)
        print(" Connexion à PostgreSQL réussie")
        return conn
    except Exception as e:
        print(f" Erreur de connexion à PostgreSQL : {e}")
        return None


def save_file_to_db(file_path, file_name):
    """Enregistre un fichier binaire dans PostgreSQL si le nom n'existe pas déjà."""
    try:
        connection = connect_db()
        if connection is None:
            return
        
        cursor = connection.cursor()

        # Vérifier si le fichier existe déjà dans la base de données
        cursor.execute("SELECT 1 FROM ferry_plot_binary_email WHERE file_name = %s", (file_name,))
        if cursor.fetchone():
            print(f"Le fichier {file_name} existe déjà dans la base de données. Ignorer l'insertion.")
            return  # Si le fichier existe déjà, on arrête ici

        # Si le fichier n'existe pas, on l'enregistre
        with open(file_path, "rb") as file:
            file_data = file.read()

        query = """
        INSERT INTO ferry_plot_binary_email (file_name, file_data, received_at)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (file_name, psycopg2.Binary(file_data), datetime.now()))
        connection.commit()

        print(f"Fichier {file_name} enregistré dans PostgreSQL.")
    
    except psycopg2.Error as err:
        print(f"Erreur PostgreSQL : {err}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def process_new_emails():
    print("Exécution de process_new_emails...")

    """Vérifie les nouveaux e-mails et traite ceux venant de SENDER_EMAIL."""
    try:
        # Connexion IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("Inbox")

        # Recherche des e-mails non lus du SENDER_EMAIL
        result, data = mail.search(None, f'(UNSEEN FROM "{SENDER_EMAIL}")')
        email_ids = data[0].split()

        if not email_ids:
            print("Aucun nouvel e-mail de", SENDER_EMAIL)
            return

        # Traitement de chaque e-mail non lu
        for email_id in email_ids:
            _, data = mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            for part in email_message.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                file_name = part.get_filename()
                if file_name:
                    file_name = email.header.decode_header(file_name)[0][0]  
                    if isinstance(file_name, bytes):
                        file_name = file_name.decode()

                    file_path = os.path.join(DOWNLOAD_DIR, file_name)
                    if not os.path.isfile(file_path):
                        with open(file_path, "wb") as f:
                            f.write(part.get_payload(decode=True))

                        # Si c'est un fichier ZIP,decompresser
                        if file_name.endswith(".zip"):
                            unzip_and_save(file_path)

                        else:
                            save_file_to_db(file_path, file_name)

        print(" Traitement des nouveaux e-mails terminé.")
    
    except Exception as e:
        print(f" Erreur : {e}")

def unzip_and_save(zip_file_path):
    """Décompresse un fichier ZIP, enregistre son contenu dans la base de données, puis supprime les fichiers."""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Extraire tous les fichiers du ZIP dans le dossier temporaire
            zip_ref.extractall(DOWNLOAD_DIR)
            print(f" Fichier ZIP {zip_file_path} extrait.")

            # Enregistrer les fichiers extraits dans la base de données
            for file_name in zip_ref.namelist():
                file_path = os.path.join(DOWNLOAD_DIR, file_name)
                save_file_to_db(file_path, file_name)

                # Supprimer le fichier après enregistrement
                os.remove(file_path)
                print(f" Fichier {file_name} supprimé après enregistrement.")

        # Supprimer le fichier ZIP après extraction
        os.remove(zip_file_path)
        print(f" Fichier ZIP {zip_file_path} supprimé après extraction.")

    except Exception as e:
        print(f" Erreur lors de la gestion du ZIP : {e}")

