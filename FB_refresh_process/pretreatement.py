import os
import logging
import select
import sys
import time
import json
import pandas as pd
import io
from datetime import datetime
from geopy.distance import geodesic
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ferry_app.settings") 

from Ferry_plot.models import Measurements
from connect import connect_db
# Connexion à la base de données
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from connect import connect_db

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_indexed_file_into_db(table_name, file_name, file_data, db_conn):
    try:
        with db_conn.cursor() as cur:
            insert_query = f"""INSERT INTO "{table_name}" (libelle, fichier) VALUES (%s, %s);"""
            cur.execute(insert_query, (file_name, file_data))
            db_conn.commit()
            logger.info(f"Fichier {file_name} inséré dans la table {table_name}.")
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion dans {table_name}: {e}")
        db_conn.rollback()

def listen_for_notifications():
    """Écoute les notifications PostgreSQL et récupère les fichiers classifiés."""
    conn = connect_db()
    if conn is None:
        logger.error("Impossible de se connecter à la base de données.")
        return

    conn.set_session(autocommit=True)
    cur = conn.cursor()

    try:
        cur.execute("LISTEN classificated_files;")
        logger.info("En attente de notifications sur le canal 'classificated_files'...")

        while True:
            if select.select([conn], [], [], 60) == ([], [], []):
                logger.info("Aucun fichier classifié reçu... Attente...")
                continue

            conn.poll()

            while conn.notifies:
                notify = conn.notifies.pop(0)

                if notify.channel != "classificated_files":
                    logger.warning(f"Notification reçue d'un autre canal : {notify.channel}")
                    continue

                try:
                    payload_data = json.loads(notify.payload)
                    new_file_id = payload_data.get("id")
                    new_file_libelle = payload_data.get("libelle")
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur de parsing JSON : {e}")
                    continue

                logger.info(f"Notification reçue ! Nouveau fichier classifié ID : {new_file_id}")

                if not new_file_id:
                    logger.warning("ID du fichier non valide ou manquant.")
                    continue

                # Déterminer la table en fonction du libellé
                table_name = None
                insert_table = None
                if "genova" in new_file_libelle.lower():
                    table_name = '"Ferry_plot_binary_classifiedgenova"'
                    insert_table = "ferry_plot_binary_indexedgenova"
                    destination = "Genova"
                elif "marseille" in new_file_libelle.lower():
                    table_name = '"Ferry_plot_binary_classifiedmarseille"'
                    insert_table = "ferry_plot_binary_indexedmarseille"
                    destination = "Marseille"

                if not table_name:
                    logger.warning("Aucune table correspondante trouvée pour ce fichier.")
                    continue

                # Récupération du fichier depuis la base de données
                query = f"SELECT libelle, fichier FROM {table_name} WHERE id = %s"
                cur.execute(query, (new_file_id,))
                result = cur.fetchone()

                if result:
                    libelle, file_binary = result
                    logger.info(f"Fichier classifié récupéré avec succès : {libelle}")

                    try:
                        # Lecture du fichier CSV en forçant le bon séparateur
                        file_content = io.BytesIO(file_binary).read().decode("utf-8", errors="replace")
                        df = pd.read_csv(io.StringIO(file_content), sep=None, engine="python", header=1)

                        if df.shape[1] == 1:
                            logger.warning("Toutes les données sont dans une seule colonne, tentative avec ',' comme séparateur.")
                            df = pd.read_csv(io.StringIO(file_content), sep=',', engine="python", header=1)

                        logger.info(f"Colonnes détectées : {df.columns.tolist()}")
                        
                        # Renommage des colonnes pH
                        df.rename(columns={'pH_Meinsberg': 'pH', 'pH_SeaFET': 'pH_Satlantic'}, inplace=True)
                        
                        # Extraction des informations du fichier pour le Ref_trip
                        depart = 'goulette' if 'goulette' in libelle.lower() else libelle.split('_to_')[0].split('_')[-1]
                        file_date = libelle.split('_')[1]
                        
                        # Ajout de la colonne Ref_trip
                        try:
                            df['Ref_trip'] = int(libelle.split('_')[0])
                        except (IndexError, ValueError):
                            df['Ref_trip'] = 0
                            logger.warning("Impossible de déterminer Ref_trip à partir du libellé, valeur par défaut 0 utilisée.")
                        
                        if 'Date' in df.columns and 'Time' in df.columns:
                            # Conversion de la colonne Date Time
                            try:
                                df['Date Time'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), errors='coerce')
                            except Exception as e:
                                logger.warning(f"Erreur lors de la conversion de Date Time: {e}. Tentative avec format par défaut.")
                                df['Date Time'] = pd.to_datetime(df['Date Time'], errors='coerce')
                            
                            # Calcul du delta T en minutes
                            df["Nbr_minutes"] = df["Date Time"].diff().dt.total_seconds().div(60).fillna(0)
                            
                            # Séparation de Date et Time
                            df['Date'] = df['Date Time'].dt.date
                            df['Time'] = df['Date Time'].dt.time
                            
                            # Suppression de la colonne Date Time originale
                            df = df.drop('Date Time', axis=1)
                        else:
                            logger.warning("Colonne 'Date Time' non trouvée dans le DataFrame")
                            df['Date'] = pd.to_datetime('today').date()
                            df['Time'] = pd.to_datetime('now').time()
                            df['Nbr_minutes'] = 0
                            
                        # Calcul de Distance et Cumul_Distance
                        if 'Latitude' in df.columns and 'Longitude' in df.columns:
                            distances = []
                            prev_lat, prev_lon = None, None
                            
                            for index, row in df.iterrows():
                                lat, lon = row['Latitude'], row['Longitude']
                                if prev_lat is not None and prev_lon is not None and pd.notnull(lat) and pd.notnull(lon):
                                    dist = geodesic((prev_lat, prev_lon), (lat, lon)).kilometers
                                else:
                                    dist = 0
                                distances.append(dist)
                                prev_lat, prev_lon = lat, lon
                                
                            df['Distance'] = distances
                            df['Cumul_Distance'] = df['Distance'].cumsum()
                            
                            # Définition de l'Area
                            def determine_area(lat, destination):
                                if pd.isnull(lat):
                                    return "Unknown"
                                    
                                if destination == "Genova":
                                    # Limites pour Genova
                                    if lat < 38.384492:
                                        return "Tunis Golf"
                                    elif lat < 40.163795:
                                        return "Tyrrhenian Sea"
                                    elif lat < 41.262529:
                                        return "The Corse"
                                    elif lat >= 42.145768:
                                        return "Genoa Golf"
                                    else:
                                        return "Unknown"
                                else:  # Marseille
                                    # Limites pour Marseille
                                    if lat < 38.384492:
                                        return "Tunis Golf"
                                    elif lat < 40.163795 and lat >= 38.384492:
                                        return "Sardinia"
                                    elif lat >= 42.145768:
                                        return "Algeroprovencal basin"
                                    else:
                                        return "Unknown"
                            
                            df['Area'] = df['Latitude'].apply(lambda x: determine_area(x, destination))
                        else:
                            logger.warning("Colonnes 'Latitude' ou 'Longitude' non trouvées dans le DataFrame")
                            df['Distance'] = 0
                            df['Cumul_Distance'] = 0
                            df['Area'] = "Unknown"
                        
                        # Traitement des colonnes QC
                        has_temp_optode = 'Temperature_Optode' in df.columns
                        
                        # Définir les paramètres et leurs colonnes de variance correspondantes
                        param_variance_map = {
                            'Salinity_SBE45': 'Variance.4',
                            'Temp_in_SBE38': 'Variance.6',
                            'Oxygen': 'Variance.7'
                        }
                        
                        if has_temp_optode:
                            param_variance_map.update({
                                'Turbidity': 'Variance.10',
                                'Chl_a': 'Variance.11'
                            })
                        else:
                            param_variance_map.update({
                                'Turbidity': 'Variance.9',
                                'Chl_a': 'Variance.10'
                            })
                        
                        # Traitement des QC pour chaque paramètre
                        for param, variance_col in param_variance_map.items():
                            if param in df.columns and variance_col in df.columns:
                                qc_values = [4]  # Premier élément toujours à 4
                                
                                for i in range(1, len(df)):
                                    v = df.loc[i, variance_col] if pd.notnull(df.loc[i, variance_col]) else 0
                                    p = df.loc[i, param] if pd.notnull(df.loc[i, param]) else 0
                                    
                                    # Définir les conditions de QC selon le paramètre
                                    if param in ['Oxygen', 'Turbidity']:
                                        cond_1 = (v >= 1) or (p == 0)
                                        cond_2 = (v >= 0.1) and (v < 1)
                                        cond_3 = (v >= 0.01) and (v < 0.1)
                                        cond_4 = (v >= 0.001) and (v < 0.01)
                                    else:
                                        cond_1 = (v >= 0.1) or (p == 0)
                                        cond_2 = (v >= 0.01) and (v < 0.1)
                                        cond_3 = (v >= 0.001) and (v < 0.01)
                                        cond_4 = (v >= 0.0001) and (v < 0.001)
                                    
                                    # Assigner une valeur QC en fonction des conditions
                                    if param == 'Oxygen':
                                        if cond_4 or cond_3 or cond_2:
                                            qc_values.append(1)
                                        elif cond_1:
                                            qc_values.append(4)
                                        else:
                                            qc_values.append(1)
                                    elif param == 'Temp_in_SBE38':
                                        if cond_4 or cond_3:
                                            qc_values.append(1)
                                        elif cond_2:
                                            qc_values.append(2)
                                        elif cond_1:
                                            qc_values.append(4)
                                        else:
                                            qc_values.append(1)
                                    elif param == 'Turbidity':
                                        if cond_4 or cond_3:
                                            qc_values.append(1)
                                        elif cond_2:
                                            qc_values.append(2)
                                        elif cond_1:
                                            qc_values.append(4)
                                        else:
                                            qc_values.append(1)
                                    else:
                                        if cond_4:
                                            qc_values.append(1)
                                        elif cond_3:
                                            qc_values.append(2)
                                        elif cond_2:
                                            qc_values.append(3)
                                        elif cond_1:
                                            qc_values.append(4)
                                        else:
                                            qc_values.append(0 if param == 'Chl_a' else 1)
                                
                                df[f"QC_{param}"] = qc_values
                            else:
                                logger.warning(f"Colonne {param} ou {variance_col} non trouvée dans le DataFrame")
                        
                        # Conversion de l'oxygène si nécessaire (micromol/l à ml/l)
                        if 'Oxygen' in df.columns:
                            df['Oxygen'] = df['Oxygen'].apply(lambda x: x * 0.022391 if pd.notnull(x) else x)
                        
                        # Renommage des colonnes de variance
                        variance_rename = {
                            'Variance': 'Variance_course',
                            'Variance.1': 'Variance_Speed',
                            'Variance.2': 'Variance_Temp_SBE45',
                            'Variance.3': 'Variance_Cond_SBE45',
                            'Variance.4': 'Variance_Salinity_SBE45',
                            'Variance.5': 'Variance_SoundVel_SBE45',
                            'Variance.6': 'Variance_Temp_in_SBE38',
                            'Variance.7': 'Variance_Oxygen',
                            'Variance.8': 'Variance_Saturation'
                        }
                        
                        if has_temp_optode:
                            variance_rename.update({
                                'Variance.9': 'Variance_Temperature_Optode',
                                'Variance.10': 'Variance_Turbidity',
                                'Variance.11': 'Variance_Chl_a',
                                'Variance.12': 'Variance_pH',
                                'Variance.14': 'Variance_pH_Satlantic',
                                'Variance.16': 'Variance_pressure',
                                'Variance.17': 'Variance_flow_in',
                                'Variance.18': 'Variance_flow_main',
                                'Variance.19': 'Variance_flow_pH',
                                'Variance.20': 'Variance_flow_pCO2',
                                'Variance.21': 'Variance_halffull',
                                'Variance.22': 'Variance_full'
                            })
                        else:
                            variance_rename.update({
                                'Variance.9': 'Variance_Turbidity',
                                'Variance.10': 'Variance_Chl_a',
                                'Variance.11': 'Variance_pH',
                                'Variance.12': 'Variance_pH_Satlantic',
                                'Variance.13': 'Variance_pressure',
                                'Variance.14': 'Variance_flow_in',
                                'Variance.15': 'Variance_flow_main',
                                'Variance.16': 'Variance_flow_pH',
                                'Variance.17': 'Variance_flow_pCO2',
                                'Variance.18': 'Variance_halffull'
                            })
                            
                        # Renommer les colonnes de variance
                        df.rename(columns=variance_rename, inplace=True)
                        
                        # Réorganisation des colonnes pour avoir l'ordre souhaité
                        desired_columns = [
                            'Ref_trip', 'Date', 'Time', 'Nbr_minutes', 'Latitude', 'Longitude', 
                            'Distance', 'Cumul_Distance', 'Area',
                            'Salinity_SBE45', 'QC_Salinity_SBE45', 'Variance_Salinity_SBE45',
                            'Temp_in_SBE38', 'QC_Temp_in_SBE38', 'Variance_Temp_in_SBE38',
                            'Oxygen', 'QC_Oxygen', 'Variance_Oxygen',
                            'Turbidity', 'QC_Turbidity', 'Variance_Turbidity',
                            'Chl_a', 'QC_Chl_a', 'Variance_Chl_a',
                            'Course', 'Variance_course',
                            'Speed', 'Variance_Speed',
                            'Temp_SBE45', 'Variance_Temp_SBE45',
                            'Cond_SBE45', 'Variance_Cond_SBE45',
                            'SoundVel_SBE45', 'Variance_SoundVel_SBE45',
                            'Saturation', 'Variance_Saturation',
                            'pH', 'Variance_pH',
                            'pH_Satlantic', 'Variance_pH_Satlantic',
                            'pressure', 'Variance_pressure',
                            'flow_in', 'Variance_flow_in',
                            'flow_main', 'Variance_flow_main',
                            'flow_pH', 'Variance_flow_pH',
                            'flow_pCO2', 'Variance_flow_pCO2',
                            'halffull', 'Variance_halffull'
                        ]
                        
                        # Filtrer pour ne garder que les colonnes qui existent réellement dans le DataFrame
                        final_columns = [col for col in desired_columns if col in df.columns]
                        
                        # Ajouter les colonnes qui ne sont pas dans desired_columns mais qui sont dans df
                        for col in df.columns:
                            if col not in final_columns:
                                final_columns.append(col)
                        
                        # Réorganiser les colonnes
                        df = df[final_columns]
                        
                        # Conversion du DataFrame en fichier CSV binaire pour stockage en BDD
                        buffer = io.StringIO()
                        df.to_csv(buffer, index=False, encoding="utf-8-sig")
                        file_data = buffer.getvalue().encode("utf-8")  # Convertir en binaire

                        # Insertion du fichier traité dans la base de données
                        insert_indexed_file_into_db(insert_table, new_file_libelle, file_data, conn)
                        logger.info(f"Fichier traité inséré dans la base de données sous le libellé : {new_file_libelle}")
                        
                        # Insertion des données dans le modèle Measurements
                        insert_into_measurements(df)
                        logger.info(f"Données du fichier {new_file_libelle} insérées dans le modèle Measurements.")

                    except Exception as e:
                        logger.error(f"Erreur lors du traitement du fichier : {e}", exc_info=True)
                        
                else:
                    logger.warning(f"Aucun fichier classifié trouvé pour l'ID : {new_file_id}")
                    
    except KeyboardInterrupt:
        logger.info("Arrêt de l'écoute des notifications.")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}", exc_info=True)
        time.sleep(5)
    finally:
        cur.close()
        conn.close()
        logger.info("Connexion PostgreSQL fermée.")


def insert_into_measurements(df):
    """Insère les lignes du DataFrame dans le modèle Measurements."""
    measurements = []
    # Remap les colonnes du DataFrame pour correspondre au nom exact du modèle
    df.rename(columns=lambda x: x[0].upper() + x[1:] if x.lower() in [f.name.lower() for f in Measurements._meta.fields] else x, inplace=True)

    for _, row in df.iterrows():
        try:
            measurement = Measurements(
                Ref_trip=row.get("Ref_trip", 0),
                Date=row.get("Date"),
                Time=row.get("Time"),
                Nbr_minutes=row.get("Nbr_minutes", 0),
                Latitude=row.get("Latitude", 0),
                Longitude=row.get("Longitude", 0),
                Distance=row.get("Distance", 0),
                Cumul_Distance=row.get("Cumul_Distance", 0),
                Area=row.get("Area", ""),
                Salinity_SBE45=row.get("Salinity_SBE45", 0),
                QC_Salinity_SBE45=row.get("QC_Salinity_SBE45", 0),
                Variance_Salinity_SBE45=row.get("Variance_Salinity_SBE45", 0),
                Temp_in_SBE38=row.get("Temp_in_SBE38", 0),
                QC_Temp_in_SBE38=row.get("QC_Temp_in_SBE38", 0),
                Variance_Temp_in_SBE38=row.get("Variance_Temp_in_SBE38", 0),
                Oxygen=row.get("Oxygen", 0),
                QC_Oxygen=row.get("QC_Oxygen", 0),
                Variance_Oxygen=row.get("Variance_Oxygen", 0),
                Turbidity=row.get("Turbidity", 0),
                QC_Turbidity=row.get("QC_Turbidity", 0),
                Variance_Turbidity=row.get("Variance_Turbidity", 0),
                Chl_a=row.get("Chl_a", 0),
                QC_Chl_a=row.get("QC_Chl_a", 0),
                Variance_Chl_a=row.get("Variance_Chl_a", 0),
                Course=row.get("Course", 0),
                Variance_course=row.get("Variance_course", 0),
                Speed=row.get("Speed", 0),
                Variance_Speed=row.get("Variance_Speed", 0),
                Temp_SBE45=row.get("Temp_SBE45", 0),
                Variance_Temp_SBE45=row.get("Variance_Temp_SBE45", 0),
                Cond_SBE45=row.get("Cond_SBE45", 0),
                Variance_Cond_SBE45=row.get("Variance_Cond_SBE45", 0),
                SoundVel_SBE45=row.get("SoundVel_SBE45", 0),
                Variance_SoundVel_SBE45=row.get("Variance_SoundVel_SBE45", 0),
                Saturation=row.get("Saturation", 0),
                Variance_Saturation=row.get("Variance_Saturation", 0),
                pH=row.get("pH", 0),
                Variance_pH=row.get("Variance_pH", 0),
                pH_Satlantic=row.get("pH_Satlantic", 0),
                Variance_pH_Satlantic=row.get("Variance_pH_Satlantic", 0),
                pressure=row.get("pressure", 0),
                Variance_pressure=row.get("Variance_pressure", 0),
                flow_in=row.get("flow_in", 0),
                Variance_flow_in=row.get("Variance_flow_in", 0),
                flow_main=row.get("flow_main", 0),
                Variance_flow_main=row.get("Variance_flow_main", 0),
                flow_pH=row.get("flow_pH", 0),
                Variance_flow_pH=row.get("Variance_flow_pH", 0),
                flow_pCO2=row.get("flow_pCO2", 0),
                Variance_flow_pCO2=row.get("Variance_flow_pCO2", 0),
                halffull=row.get("halffull", 0),
                Variance_halffull=row.get("Variance_halffull", 0),
            )
            measurements.append(measurement)
        except Exception as e:
            logger.warning(f"Erreur lors de la préparation d'une ligne pour Measurements : {e}")

    if measurements:
        try:
            Measurements.objects.bulk_create(measurements, batch_size=1000)
            logger.info(f"{len(measurements)} lignes insérées dans Measurements.")
        except Exception as e:
            logger.error(f"Erreur lors de l'insertion dans Measurements : {e}", exc_info=True)

