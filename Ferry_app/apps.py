from django.apps import AppConfig
import threading
import importlib.util
import sys
import time

class FerryAppConfig(AppConfig):
    name = 'Ferry_app'  

    # Dictionnaire pour stocker les threads en cours
    running_threads = {}

    def ready(self):
        print("=============================  AppConfig FerryAppConfig chargé ======================================")  

        # Vérification et démarrage du script d'import des emails
        if "email_check_thread" not in FerryAppConfig.running_threads or not FerryAppConfig.running_threads["email_check_thread"].is_alive():
            print(" ---------------------- Démarrage du script de vérification des emails ---------------------")
            self.start_email_check(r'C:\dsi3\stage Pfe\ferrybox-2\FB_refresh_process\2_E-mail_download.py', "email_download", 60)
        
        # Vérification et démarrage du script de classification
        if "classification_thread" not in FerryAppConfig.running_threads or not FerryAppConfig.running_threads["classification_thread"].is_alive():
            print("------------------------ Démarrage du script classification --------------------")
            self.start_script(r'C:\dsi3\stage Pfe\ferrybox-2\FB_refresh_process\classification.py', "classification")

        # Vérification et démarrage du script de prétraitement
        if "pretreatement_thread" not in FerryAppConfig.running_threads or not FerryAppConfig.running_threads["pretreatement_thread"].is_alive():
            print(" ------------------------ Démarrage du pretreatement ---------------------")
            self.start_script(r'C:\dsi3\stage Pfe\ferrybox-2\FB_refresh_process\pretreatement.py', "pretreatement")
               # Vérification et démarrage du script de time series
        if "timeSeries_thread" not in FerryAppConfig.running_threads or not FerryAppConfig.running_threads["timeSeries_thread"].is_alive():
            print(" ------------------------ Démarrage du timeSeries ---------------------")
            self.start_script(r'C:\dsi3\stage Pfe\ferrybox-2\FB_refresh_process\timeSeries.py', "timeSeries")
        if "metadata_thread" not in FerryAppConfig.running_threads or not FerryAppConfig.running_threads["metadata_thread"].is_alive():
            print(" ------------------------ Démarrage du metadata ---------------------")
            self.start_script(r'C:\dsi3\stage Pfe\ferrybox-2\FB_refresh_process\metadata.py', "metadata")

    def start_script(self, module_path, module_name):
          """Charge et exécute un script de manière dynamique."""
          thread_key = f"{module_name}_thread"

          if thread_key in FerryAppConfig.running_threads:
             existing_thread = FerryAppConfig.running_threads[thread_key]
             if existing_thread.is_alive():
               print(f"Le thread pour '{module_name}' est déjà en cours d'exécution.")
               return

          try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            print("----------------- le module-----------------",module)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            thread = threading.Thread(target=module.listen_for_notifications, daemon=True)
            thread.start()
        
            FerryAppConfig.running_threads[thread_key] = thread
            print(f"Script '{module_name}' chargé avec succès et en cours d'exécution.")
          except Exception as e:
           print(f"Erreur lors du chargement de '{module_name}' : {e}")

            

    def start_email_check(self, module_path, module_name, interval):
        """Démarre un script qui s'exécute périodiquement pour vérifier les emails."""
        def email_checker():
            while True:
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    if hasattr(module, "process_new_emails"):
                        module.process_new_emails()
                    else:
                        print(f"Le module '{module_name}' ne contient pas de fonction ' process_new_emails'.")

                except Exception as e:
                    print(f"Erreur lors de l'exécution du script '{module_name}' : {e}")
                
                time.sleep(interval)  

        thread = threading.Thread(target=email_checker, daemon=True)
        thread.start()
        
        FerryAppConfig.running_threads["email_check_thread"] = thread
        print(f"Script de vérification des emails '{module_name}' lancé avec succès.")

