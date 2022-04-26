"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import environ
import django_heroku
import datetime

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# Load the environment variables.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
DJANGO_ENV = os.environ.get('DJANGO_ENV')

env = environ.Env()

if DJANGO_ENV == None or DJANGO_ENV == "":
    DJANGO_ENV = 'dev'
    ENV_FILE = '.env.dev'
    DEBUG = True
else:
    ENV_FILE = '.env.'+DJANGO_ENV


DEBUG = True
environ.Env.read_env(os.path.join(BASE_DIR, ENV_FILE))

# DEBUG=eval(env('DEBUG'))


# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

AUTH_USER_MODEL = 'authentication.User'


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)08%828jjep%hpdilb*cs$^^2y1)hf(hl2w-5c843dwq4pj^2h'
MASTER_KEY = env('MASTER_KEY')
TEST_KEY = env('TEST_KEY')

ALLOWED_HOSTS = [
    '.herokuapp.com',
    'tactictrade-api.herokuapp.com',
    '*'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'rest_framework',
    'rest_framework_swagger',
    
    'drf_yasg2',
    # 'dbbackup', # Apps for doing the backups
    'gridfs_storage',
    'django_filters',
    'drf_multiple_model',
    'gunicorn',
    'apps.authentication',
    'apps.setting',
    'apps.strategy',
    'apps.trading',
    'apps.transaction',
    'apps.broker',
    'apps.notification',

   
]


# SCHEDULER
WHITENOISE_USE_FINDERS = True


REST_FRAMEWORK = {
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_PERMISSION_CLASSES': ( 'rest_framework.permissions.IsAuthenticated', ), #!TODO Active this por production
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',

    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ],

}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(hours=6),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
}

JWT_AUTH = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'JWT_ALLOW_REFRESH': True,
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7),
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [

        ],
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


CSRF_COOKIE_DOMAIN = ['herokuapp.com']
WSGI_APPLICATION = 'backend.wsgi.application'
DB_NAME = env('DB_NAME')

if env('DB_HOST').find('mongodb+srv') == -1:

    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': env('DB_NAME'),
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': env('DB_HOST'),
                'port': 27017,
                'username': env('DB_USERNAME'),
                'password': env('DB_PASSWORD'),

            },
        }}

else:

    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': env('DB_NAME'),
            'CLIENT': {
                'host': env('DB_HOST'),
                'username': env('DB_USERNAME'),
                'password': env('DB_PASSWORD')
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'

# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )


STATIC_ROOT = str(BASE_DIR.joinpath('staticfiles'))
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads/images')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Extra lookup directories for collectstatic to find static files

#  Add configuration for static files storage using whitenoise

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL SERVICE
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

django_heroku.settings(locals())

# Storage inside of mongo db GridFSStorage
UPLOADED_FILES_USE_URL = True
BASE_URL = env('BASE_URL')


# Auth Social Media.
SOCIAL_SECRET = env('SOCIAL_SECRET')
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')

IMAGE_KIT_URL_UPLOAD = env('IMAGE_KIT_URL_UPLOAD')
IMAGE_KIT_TOKEN = env('IMAGE_KIT_TOKEN')
IMAGE_KIT_TAGS = DJANGO_ENV + '_' + DB_NAME


DATA_UPLOAD_MAX_NUMBER_FIELDS = None
DATA_UPLOAD_MAX_MEMORY_SIZE = None

ALPACA_BROKER_TEST_SECRET_KEY = env('ALPACA_BROKER_TEST_SECRET_KEY')
ALPACA_BROKER_TEST_API_KEY_ID = env('ALPACA_BROKER_TEST_API_KEY_ID')

## ENCRYPT DATA CONFIGURATION 


#! BACKUP DATABASE CONFIGURATION
#TODO BackupDB Finish this configuration is pending
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR / 'backup'}


DBBACKUP_CONNECTORS = {
    'default': {
        'USER': env('DB_USERNAME'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'AUTH_SOURCE':  env('DB_USERNAME'),
    }
}

#! TEST CONTROLLERS
# Active or Disabled Test.

# apps.authentication
test_register_user = True
test_login_user_not_verified = True
test_login_user_verified = True
test_create_user = True
test_create_super_user = True


test_message_create_user_when_not_user_name_is_supplied = False
test_create_user_when_not_user_name_is_supplied = False
test_create_user_when_not_user_email_is_supplied = False
test_message_create_user_when_not_user_email_is_supplied = False

# apps.trading
test_create_broker_alpaca = False
test_trading_config_is_crypto_alpaca_short = False

test_trading_config_alpaca_short_not_fractional = False
test_short_crypto = False
test_long_buy_crypto = False
test_calibrate_spread_not_crypto = False

# Test the trading parameters.
    # Test for Open Long Order 
test_trading_open_long = False
test_trading_open_short = False


### MONITORING WIHTH SENTRY. 

sentry_sdk.init(
    dsn="https://99d5e1e15517491488bd3017af9f4953@o1217629.ingest.sentry.io/6359657",
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)



#! PUSH NOTIFICATIONS ---------------------------------------------------------------------- >>

PUSH_NOTIFICATIONS_FIREBASE_CLOUD_MESSAGE_TOKEN = env('PUSH_NOTIFICATIONS_FIREBASE_CLOUD_MESSAGE_TOKEN')

#! <<