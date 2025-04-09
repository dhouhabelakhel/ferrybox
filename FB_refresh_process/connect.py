import psycopg2
from django.conf import settings

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