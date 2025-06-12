import unittest
from unittest.mock import Mock, patch, MagicMock, call
import psycopg2
import zipfile
import io
from datetime import datetime
import email
import imaplib
import os
import sys

# Import du module à tester
from email_processor import connect_db, save_file_to_db, process_new_emails, handle_zip_file

class TestEmailProcessor(unittest.TestCase):
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.test_file_name = "test_file.txt"
        self.test_file_data = b"test file content"
        self.test_zip_data = self.create_test_zip()
    
    def create_test_zip(self):
        """Crée un fichier ZIP de test en mémoire"""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr("file1.txt", "contenu du fichier 1")
            zip_file.writestr("file2.txt", "contenu du fichier 2")
        return zip_buffer.getvalue()

    @patch('email_processor.settings')
    @patch('psycopg2.connect')
    def test_connect_db_success(self, mock_connect, mock_settings):
        """Test de connexion réussie à la base de données"""
        # Configuration des mocks
        mock_settings.DATABASES = {
            'default': {
                'NAME': 'test_db',
                'USER': 'test_user',
                'PASSWORD': 'test_pass',
                'HOST': 'localhost',
                'PORT': '5432'
            }
        }
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        # Test de la fonction
        result = connect_db()
        
        # Vérifications
        self.assertEqual(result, mock_connection)
        mock_connect.assert_called_once_with(
            dbname='test_db',
            user='test_user',
            password='test_pass',
            host='localhost',
            port='5432'
        )

    @patch('email_processor.settings')
    @patch('psycopg2.connect')
    def test_connect_db_failure(self, mock_connect, mock_settings):
        """Test d'échec de connexion à la base de données"""
        mock_settings.DATABASES = {'default': {}}
        mock_connect.side_effect = psycopg2.Error("Connection failed")
        
        result = connect_db()
        
        self.assertIsNone(result)

    @patch('email_processor.get_channel_layer')
    @patch('email_processor.async_to_sync')
    @patch('email_processor.connect_db')
    def test_save_file_to_db_new_file(self, mock_connect_db, mock_async_to_sync, mock_get_channel_layer):
        """Test d'enregistrement d'un nouveau fichier"""
        # Configuration des mocks
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Fichier n'existe pas
        mock_connect_db.return_value = mock_connection
        
        mock_channel_layer = Mock()
        mock_get_channel_layer.return_value = mock_channel_layer
        mock_group_send = Mock()
        mock_async_to_sync.return_value = mock_group_send
        
        # Test de la fonction
        save_file_to_db(self.test_file_name, self.test_file_data)
        
        # Vérifications
        mock_cursor.execute.assert_any_call(
            "SELECT 1 FROM ferry_plot_binary_email WHERE file_name = %s", 
            (self.test_file_name,)
        )
        
        # Vérifier que l'INSERT a été appelé
        insert_calls = [call for call in mock_cursor.execute.call_args_list 
                       if call[0][0].startswith("INSERT")]
        self.assertEqual(len(insert_calls), 1)
        
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('email_processor.connect_db')
    def test_save_file_to_db_existing_file(self, mock_connect_db):
        """Test avec un fichier qui existe déjà"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = True  # Fichier existe déjà
        mock_connect_db.return_value = mock_connection
        
        save_file_to_db(self.test_file_name, self.test_file_data)
        
        # Vérifier qu'aucun INSERT n'a été fait
        insert_calls = [call for call in mock_cursor.execute.call_args_list 
                       if len(call[0]) > 0 and call[0][0].startswith("INSERT")]
        self.assertEqual(len(insert_calls), 0)

    @patch('email_processor.save_file_to_db')
    def test_handle_zip_file(self, mock_save_file_to_db):
        """Test de gestion des fichiers ZIP"""
        handle_zip_file("test.zip", self.test_zip_data)
        
        # Vérifier que save_file_to_db a été appelé pour chaque fichier dans le ZIP
        self.assertEqual(mock_save_file_to_db.call_count, 2)
        
        calls = mock_save_file_to_db.call_args_list
        call_files = [call[0][0] for call in calls]  # Récupérer les noms de fichiers
        
        self.assertIn("file1.txt", call_files)
        self.assertIn("file2.txt", call_files)

    @patch('email_processor.logger')
    @patch('email_processor.save_file_to_db')
    def test_handle_zip_file_error(self, mock_save_file_to_db, mock_logger):
        """Test de gestion d'erreur avec fichier ZIP corrompu"""
        # Données ZIP corrompues
        corrupted_zip_data = b"not a zip file"
        
        handle_zip_file("corrupted.zip", corrupted_zip_data)
        
        # Vérifier qu'une erreur a été loggée
        mock_logger.error.assert_called()

    @patch('email_processor.settings')
    @patch('imaplib.IMAP4_SSL')
    @patch('email_processor.save_file_to_db')
    @patch('email_processor.handle_zip_file')
    def test_process_new_emails(self, mock_handle_zip, mock_save_file, mock_imap, mock_settings):
        """Test du traitement des nouveaux emails"""
        # Configuration des settings
        mock_settings.EMAIL_HOST_USER = "test@example.com"
        mock_settings.EMAIL_HOST_PASSWORD = "password"
        
        # Configuration du mock IMAP
        mock_mail = Mock()
        mock_imap.return_value = mock_mail
        
        # Simuler la recherche d'emails
        mock_mail.search.return_value = ('OK', [b'1 2'])
        
        # Créer un email de test avec pièce jointe
        test_email = self.create_test_email_with_attachment()
        mock_mail.fetch.return_value = ('OK', [(None, test_email)])
        
        process_new_emails()
        
        # Vérifications
        mock_mail.login.assert_called_once_with("test@example.com", "password")
        mock_mail.select.assert_called()
        mock_mail.search.assert_called()
        mock_mail.logout.assert_called_once()

    def create_test_email_with_attachment(self):
        """Crée un email de test avec pièce jointe"""
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = "ferryboxinstm@gmail.com"
        msg['To'] = "test@example.com"
        msg['Subject'] = "Test Email"
        
        # Ajouter une pièce jointe texte
        attachment = email.mime.text.MIMEText("test content")
        attachment.add_header('Content-Disposition', 'attachment', filename='test.txt')
        msg.attach(attachment)
        
        return msg.as_bytes()

    @patch('email_processor.logger')
    @patch('email_processor.settings')
    @patch('imaplib.IMAP4_SSL')
    def test_process_new_emails_connection_error(self, mock_imap, mock_settings, mock_logger):
        """Test de gestion d'erreur de connexion IMAP"""
        mock_settings.EMAIL_HOST_USER = "test@example.com"
        mock_settings.EMAIL_HOST_PASSWORD = "password"
        
        # Simuler une erreur de connexion
        mock_imap.side_effect = Exception("Connection failed")
        
        process_new_emails()
        
        # Vérifier qu'une erreur a été loggée
        mock_logger.error.assert_called()

    @patch('email_processor.save_file_to_db')
    @patch('email_processor.connect_db')
    def test_database_error_handling(self, mock_connect_db, mock_save_file_to_db):
        """Test de gestion des erreurs de base de données"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Database error")
        mock_connect_db.return_value = mock_connection
        
        # La fonction ne doit pas lever d'exception
        try:
            save_file_to_db(self.test_file_name, self.test_file_data)
        except Exception as e:
            self.fail(f"save_file_to_db raised an exception: {e}")
        
        # Vérifier que les ressources sont nettoyées
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Tests d'intégration plus complexes"""
    
    @patch('email_processor.settings')
    @patch('psycopg2.connect')
    @patch('imaplib.IMAP4_SSL')
    def test_full_email_processing_workflow(self, mock_imap, mock_connect, mock_settings):
        """Test du workflow complet de traitement d'email"""
        # Configuration complète des mocks
        self.setup_full_mocks(mock_settings, mock_connect, mock_imap)
        
        # Exécuter le processus complet
        process_new_emails()
        
        # Vérifications que le workflow s'est bien déroulé
        mock_imap.assert_called_once_with("imap.gmail.com", 993)
    
    def setup_full_mocks(self, mock_settings, mock_connect, mock_imap):
        """Configuration complète des mocks pour les tests d'intégration"""
        # Configuration settings
        mock_settings.EMAIL_HOST_USER = "test@example.com"
        mock_settings.EMAIL_HOST_PASSWORD = "password"
        mock_settings.DATABASES = {
            'default': {
                'NAME': 'test_db',
                'USER': 'test_user',
                'PASSWORD': 'test_pass',
                'HOST': 'localhost',
                'PORT': '5432'
            }
        }
        
        # Configuration base de données
        mock_db_connection = Mock()
        mock_cursor = Mock()
        mock_db_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value = mock_db_connection
        
        # Configuration IMAP
        mock_mail = Mock()
        mock_imap.return_value = mock_mail
        mock_mail.search.return_value = ('OK', [b'1'])
        
        test_email = self.create_simple_test_email()
        mock_mail.fetch.return_value = ('OK', [(None, test_email)])
    
    def create_simple_test_email(self):
        """Crée un email simple pour les tests"""
        return b'From: ferryboxinstm@gmail.com\r\nTo: test@example.com\r\nSubject: Test\r\n\r\nTest body'


# Classe pour simuler Django settings si pas disponible
class MockDjangoSettings:
    """Mock des settings Django pour les tests autonomes"""
    EMAIL_HOST_USER = "test@example.com"
    EMAIL_HOST_PASSWORD = "test_password"
    DATABASES = {
        'default': {
            'NAME': 'test_db',
            'USER': 'test_user',
            'PASSWORD': 'test_pass',
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }


def setup_django_mock():
    """Configure un mock Django pour les tests autonomes"""
    # Si Django n'est pas disponible, créer un mock
    try:
        import django
        from django.conf import settings
        if not settings.configured:
            settings.configure(
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.postgresql',
                        'NAME': 'test_db',
                        'USER': 'test_user',
                        'PASSWORD': 'test_pass',
                        'HOST': 'localhost',
                        'PORT': '5432',
                    }
                },
                EMAIL_HOST_USER='test@example.com',
                EMAIL_HOST_PASSWORD='test_password',
                USE_TZ=True,
                INSTALLED_APPS=['channels'],
            )
    except ImportError:
        # Si Django n'est pas installé, utilisons un mock
        import sys
        sys.modules['django'] = Mock()
        sys.modules['django.conf'] = Mock()
        sys.modules['django.conf'].settings = MockDjangoSettings()
        sys.modules['asgiref'] = Mock()
        sys.modules['asgiref.sync'] = Mock()
        sys.modules['channels'] = Mock()
        sys.modules['channels.layers'] = Mock()


def run_tests():
    """Fonction pour exécuter tous les tests"""
    # Configuration Django mock si nécessaire
    setup_django_mock()
    
    # Créer une suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter tous les tests
    suite.addTests(loader.loadTestsFromTestCase(TestEmailProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Configuration pour les tests
    print("=== Début des tests du processeur d'emails ===")
    print("Structure des fichiers attendue:")
    print("├── email_processor.py  # Votre script original")
    print("├── test_email_processor.py  # Ce script de test")
    print()
    
    # Vérifier que le module principal existe
    try:
        import email_processor
        print("✅ Module email_processor trouvé")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Assurez-vous que votre script s'appelle 'email_processor.py'")
        print("Ou modifiez la ligne d'import au début de ce fichier de test")
        sys.exit(1)
    
    # Exécuter les tests
    success = run_tests()
    
    if success:
        print("\n✅ Tous les tests sont passés avec succès!")
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les détails ci-dessus.")
    
    print("=== Fin des tests ===")