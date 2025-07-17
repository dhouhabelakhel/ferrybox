# 🌊 Ferrybox Platform

<div align="center">

![Ferrybox Platform](https://img.shields.io/badge/Platform-Ferrybox-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?style=for-the-badge&logo=django)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**Plateforme web de traitement automatisé et de visualisation interactive des données océanographiques collectées via les systèmes Ferrybox embarqués sur des ferries commerciaux.**

[🚀 Démo en ligne](https://ferrybox.onrender.com/)

</div>

---

## 📋 Table des matières

- [🎯 Aperçu](#-aperçu)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [⚡ Installation rapide](#-installation-rapide)
- [🔧 Configuration](#-configuration)
- [📊 Utilisation](#-utilisation)
- [🤝 Contribution](#-contribution)
- [📄 Licence](#-licence)

---

## 🎯 Aperçu

La **Ferrybox Platform** est une solution complète développée par l'**INSTM** (Institut National des Sciences et Technologies de la Mer, Tunisie) pour automatiser la collecte, le traitement et la visualisation des données océanographiques en temps réel.

### 🌟 Pourquoi cette plateforme ?

- **Automatisation complète** : Traitement automatique des données depuis la réception email jusqu'à la visualisation
- **Temps réel** : Monitoring en direct avec notifications WebSocket
- **Visualisation avancée** : Cartes interactives, transects, séries temporelles
- **Sécurité** : Authentification JWT et gestion des rôles
- **Scalabilité** : Architecture modulaire et extensible

---

## ✨ Fonctionnalités

### 📥 Traitement automatisé
- ✅ Réception automatique des emails Ferrybox
- ✅ Extraction et validation des métadonnées
- ✅ Transformation en séries temporelles
- ✅ Détection des doublons et gestion d'erreurs

### 📊 Visualisation interactive
- 🗺️ **Cartes Leaflet** avec routes des ferries
- 📈 **Graphiques dynamiques** (Plotly, Chart.js)
- 🔍 **Transects par paramètre** et date
- 📊 **Heatmaps** et séries temporelles

### 🔔 Notifications temps réel
- 📱 **WebSocket** pour les mises à jour instantanées
- 📧 **Emails automatiques** pour les demandes
- 🔊 **Alertes sonores** optionnelles
- 📝 **Historique complet** des événements

### 🛡️ Sécurité et gestion
- 🔐 **Authentification JWT** + Sessions
- 👥 **Gestion des rôles** (Admin, Chercheur, Utilisateur)
- 📋 **Système de demandes** avec validation
- 🔍 **Logs détaillés** et monitoring

---

## 🏗️ Architecture

### Stack technique

| Composant | Technologies |
|-----------|-------------|
| **Backend** | Python 3.11, Django 4.2, Django REST Framework |
| **Frontend** | Django Templates, JavaScript ES6+ |
| **Base de données** | PostgreSQL 14+ |
| **Visualisation** | Leaflet.js, Chart.js |
| **Temps réel** | Django Channels, WebSockets |
| **Traitement** | Pandas, NumPy, Celery |


## ⚡ Installation rapide

### Prérequis

- Python 3.11+
- PostgreSQL 14+
- Redis (pour Celery)
- Node.js 16+ (optionnel)

### Installation avec Conda

```bash
# 1. Cloner le projet
git clone https://github.com/instm/ferrybox-platform.git
cd ferrybox-platform

# 2. Créer l'environnement
conda create -n ferrybox_env python=3.11
conda activate ferrybox_env

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# 5. Base de données
python manage.py migrate
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```



## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` basé sur `.env.example` :

```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/ferrybox

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,ferrybox.instm.tn

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (pour Celery)
REDIS_URL=redis://localhost:6379/0
```








## 📊 Utilisation

### Interface d'administration

Accédez à l'interface admin : `http://localhost:8000/admin/`

- **Gestion des utilisateurs** : Créer/modifier les comptes
- **Monitoring** : Suivre les traitements en cours
- **Configuration** : Paramètres de l'application

### API REST

La plateforme expose une API REST complète :

```python
# Exemple d'utilisation
import requests

# Authentification
response = requests.post('http://localhost:8000/api/auth/login/', {
    'username': 'user@example.com',
    'password': 'password'
})
token = response.json()['token']

# Récupérer les données
headers = {'Authorization': f'Bearer {token}'}
data = requests.get('http://localhost:8000/api/data/', headers=headers)
```

### Traitement des données

Le pipeline de traitement suit ces étapes :

1. **Réception** : Emails avec fichiers Ferrybox
2. **Extraction** : Métadonnées et données brutes
3. **Validation** : Contrôle qualité automatique
4. **Transformation** : Séries temporelles et géolocalisation
5. **Stockage** : Base de données PostgreSQL
6. **Notification** : Alerts temps réel

---

## 🤝 Contribution

### Guide de contribution

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### Standards de code

- **PEP 8** pour Python
- **ESLint** pour JavaScript
- **Tests** obligatoires pour nouvelles fonctionnalités
- **Documentation** pour les API



---

## 📞 Support

### Contacts

- **Développeur** : dhouhabelakhel2001@gmail.com





## 🙏 Remerciements

- **INSTM** pour le support institutionnel
- **Communauté Django** pour le framework
- **Contributeurs** du projet open source
- **Équipe de recherche** pour les feedbacks

---

<div align="center">

**Fait avec ❤️ par l'équipe INSTM**

[⬆ Retour en haut](#-ferrybox-platform)

</div>
