import os
from decouple import config
from unipath import Path
import dj_database_url
from Ferry_plot.log_handler import WebLogHandler
import dj_database_url
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = Path(__file__).parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
APPEND_SLASH = False
DEBUG = False

# load production server from .env
ALLOWED_HOSTS = ['localhost', '127.0.0.1', config('SERVER', default='41.229.139.78'),'*','ferrybox.onrender.com']
ASGI_APPLICATION = "Ferry_app.asgi.application"
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = [
    'Ferry_app.apps.FerryAppConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Ferry_plot',
    'channels',
    # "authentication",
    'django_mysql',
    'jquery',
    'leaflet',
    # 'chartjs',
    # 'chartjs',
    'djgeojson',
    'crispy_forms',    
    'import_export',
    'django_send_email',
    'corsheaders',

]

MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
     'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',


]

# TEMPLATE_DIR = [os.path.join(BASE_DIR, "Ferry_app/templates"),os.path.join(BASE_DIR, 'Ferry_plot/templates')]  # ROOT dir for templates
TEMPLATE_DIR = os.path.join(BASE_DIR, "Ferry_app/templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Ferry_app.wsgi.application'


DATABASES = {
        'default': dj_database_url.config(default='postgresql://dhouha:bX8WPW5C7jvmiDZe9CFfltLgErdmICs4@dpg-d1hak9ili9vc73bi5ibg-a.frankfurt-postgres.render.com/ferrybox'),
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'Ferrydb',
    #     'USER': 'postgres',
    #     'PASSWORD': 'dhouha',
    #     'HOST': '127.0.0.1',
    #     'PORT': '5432',
    # }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'Ferry_app/static'),
)

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
MEDIA_URL = '/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media_root')


ROOT_URLCONF = 'Ferry_app.urls'
LOGIN_REDIRECT_URL = "home"   # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in app/urls.py

LEAFLET_CONFIG={
    'SPATIAL_EXTENT': (5, 33.33, 15, 44.11),
    # 'SCALE':'both',
    'ATTRIBUTION_PREFIX':'Created by Tunisian FerryBox Team'
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'ferry_app.log'),
            'formatter': 'default',
        },
        'web': {
            'level': 'DEBUG',
            'class': 'Ferry_plot.log_handler.WebLogHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'Ferry_app': {
            'handlers': ['console', 'file', 'web'],
            'level': 'DEBUG',
            'propagate': False,
        },
          'classification': {  
            'handlers': ['console', 'file', 'web'],
            'level': 'DEBUG',
            'propagate': False,
        },
          'email_download': { 
            'handlers': ['console', 'file', 'web'],
            'level': 'DEBUG',
            'propagate': False,
        },
          'metadata': { 
            'handlers': ['console', 'file', 'web'],
            'level': 'DEBUG',
            'propagate': False,
        },
          'pretreatement': { 
            'handlers': ['console', 'file', 'web'],
            'level': 'DEBUG',
            'propagate': False,
        },
          'timeSeries': { 
            'handlers': ['console', 'file', 'web'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'authentication': {
        'handlers': ['console', 'file', 'web'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'authentication.views': {
        'handlers': ['console', 'file', 'web'],
        'level': 'DEBUG',
        'propagate': False,
    },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# emails settings

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'email@gmail.com'
# EMAIL_HOST_PASSWORD = 'EMAIL_PASSWORD'
# DEFAULT_FROM_EMAIL = 'webmaster@localhost'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL='tun.ferrybox@gmail.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'dhouhabelakhel2001@gmail.com'
EMAIL_HOST_PASSWORD = 'zvim jgvu wywk lnwi'
EMAIL_PORT = 587
import base64

JWT_SECRET_BASE64 = "TWFTdXBlckNsZVRyZXNMb25ndWVEZTMyQ2FyYWN0ZXJlcyEh"
JWT_SECRET = base64.b64decode(JWT_SECRET_BASE64)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",  
]
CORS_ALLOW_CREDENTIALS = True



SESSION_COOKIE_SAMESITE = None  
SESSION_COOKIE_SECURE = False   
SESSION_COOKIE_HTTPONLY = False 
SESSION_COOKIE_DOMAIN = None   
SESSION_COOKIE_AGE = 86400

CSRF_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False