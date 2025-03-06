from django.apps import AppConfig
import threading
import importlib.util
import sys

class FerryAppConfig(AppConfig):
    name = 'Ferry_app'  
    email_thread_started = False  # Verrou global pour éviter le double lancement

    def ready(self):
        print("==== AppConfig FerryAppConfig chargé ====")  # Debug
        """Lance le script de vérification des emails en arrière-plan au démarrage du serveur Django."""
        if FerryAppConfig.email_thread_started:
            print(" Vérification des emails déjà en cours. Ignoré.")
            return
        
        FerryAppConfig.email_thread_started = True  # Marquer comme démarré

        print(" Démarrage du script de vérification des emails...")  

        module_path = r'C:\dsi3\stage Pfe\ferrybox-2\FB_refresh_process\2_E-mail_download.py'
        module_name = "email_download"

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        email_download = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = email_download
        spec.loader.exec_module(email_download)

        def schedule_email_check():
            """Exécute la vérification des emails toutes les 60 secondes en boucle."""
            try:
                email_download.process_new_emails()
                print("Vérification des emails effectuée avec succès.")
            except Exception as e:
                print(f" Erreur lors de la vérification des emails : {e}")
            finally:
                threading.Timer(60, schedule_email_check).start()

        # Lancer l'exécution en arrière-plan
        thread = threading.Thread(target=schedule_email_check, daemon=True)
        thread.start()

        print(" Vérification des emails lancée en arrière-plan.")
