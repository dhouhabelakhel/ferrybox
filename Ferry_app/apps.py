from django.apps import AppConfig
import threading
import importlib.util
import sys
import time
import os
import logging

logger = logging.getLogger('Ferry_app')
class FerryAppConfig(AppConfig):
    name = 'Ferry_app'  
    default_auto_field = 'django.db.models.BigAutoField'
    path = os.path.dirname(os.path.abspath(__file__)) 
    # Dictionnaire statique pour stocker les threads en cours
    running_threads = {}
    # Variable pour suivre si ready() a déjà été exécuté
    is_ready_executed = False

    def ready(self):

        # Évite l'exécution multiple de ready() en utilisant une variable de classe
        if FerryAppConfig.is_ready_executed:
            return
        
        # Vérifier si nous sommes dans le processus principal 
        # (évite l'exécution en double lors de l'utilisation de runserver avec autoreload)
        if os.environ.get('RUN_MAIN') == 'true':
            FerryAppConfig.is_ready_executed = True
            logger.info("=============================  AppConfig FerryAppConfig chargé ======================================")  

            # Vérification et démarrage du script d'import des emails
            self.start_email_check(r'.\FB_refresh_process\email_download.py', "email_download", 60)
            
            # Vérification et démarrage du script de classification
            self.start_script(r'.\FB_refresh_process\classification.py', "classification")

            # Vérification et démarrage du script de prétraitement
            self.start_script(r'.\FB_refresh_process\pretreatement.py', "pretreatement")
            
            # Vérification et démarrage du script de time series
            self.start_script(r'.\FB_refresh_process\timeSeries.py', "timeSeries")
            
            # Vérification et démarrage du script de metadata
            self.start_script(r'.\FB_refresh_process\metadata.py', "metadata")

    def start_script(self, module_path, module_name):
        """Charge et exécute un script de manière dynamique."""
        thread_key = f"{module_name}_thread"

        if thread_key in FerryAppConfig.running_threads:
            existing_thread = FerryAppConfig.running_threads[thread_key]
            if existing_thread.is_alive():
                logger.error(f"Le thread pour '{module_name}' est déjà en cours d'exécution.")
                return
            else:
                logger.debug(f"Le thread pour '{module_name}' a été arrêté. Démarrage d'un nouveau thread.")

        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            logger.info(f"----------------- Chargement du module {module_name} -----------------")
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            thread = threading.Thread(target=module.listen_for_notifications, daemon=True)
            thread.start()
        
            FerryAppConfig.running_threads[thread_key] = thread
            logger.info(f"Script '{module_name}' chargé avec succès et en cours d'exécution.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de '{module_name}' : {e}")

    def start_email_check(self, module_path, module_name, interval):
        """Démarre un script qui s'exécute périodiquement pour vérifier les emails."""
        thread_key = "email_check_thread"
        
        if thread_key in FerryAppConfig.running_threads:
            existing_thread = FerryAppConfig.running_threads[thread_key]
            if existing_thread.is_alive():
                logger.debug(f"Le thread pour la vérification des emails est déjà en cours d'exécution.")
                return
            else:
                logger.error(f"Le thread pour la vérification des emails a été arrêté. Démarrage d'un nouveau thread.")
        
        logger.info(" ---------------------- Démarrage du script de vérification des emails ---------------------")
        
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
                        logger.error(f"Le module '{module_name}' ne contient pas de fonction 'process_new_emails'.")

                except Exception as e:
                    logger.error(f"Erreur lors de l'exécution du script '{module_name}' : {e}")
                
                time.sleep(interval)  

        thread = threading.Thread(target=email_checker, daemon=True)
        thread.start()
        
        FerryAppConfig.running_threads[thread_key] = thread
        logger.info(f"Script de vérification des emails '{module_name}' lancé avec succès.")