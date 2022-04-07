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

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
DJANGO_ENV = os.environ.get('DJANGO_ENV')


if DJANGO_ENV == None or DJANGO_ENV=="":
    DJANGO_ENV = 'dev'
    ENV_FILE = '.env.dev'
else:
    ENV_FILE = '.env.'+DJANGO_ENV

environ.Env.read_env(os.path.join(BASE_DIR, ENV_FILE))

env = environ.Env()


print('---------------- DEBUG:', env('DEBUG'))


# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Initialise environment variables


# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

AUTH_USER_MODEL = 'authentication.User'



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)08%828jjep%hpdilb*cs$^^2y1)hf(hl2w-5c843dwq4pj^2h'

print(DJANGO_ENV)


# SECRET_KEY = os.getenv('SECRET_KEY', 'change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*', 'herokudjangoapp.herokuapp.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'rest_framework',
    'rest_framework_swagger',
    'authentication',
    'whitenoise.runserver_nostatic',
    'setting',
    'drf_yasg2',
]


REST_FRAMEWORK = {
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ]
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

# AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'whitenoise.storage.CompressedManifestStaticFilesStorage',
    'django.middleware.security.SecurityMiddleware',
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# Data base configuration 
if env('DJANGO_DB') == 'sqlite3' or env('DJANGO_DB') == None or env('DJANGO_DB') == "":

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

elif env('DJANGO_DB') == 'mongodb':
    
    print("@Note-01 ---- 1722079186 -----")

    # DATABASES = {
    #    'default': {
    #       'ENGINE': 'djongo',
    #       'NAME': os.environ('MONGO_URI'),
    #    }
    # }
    
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'djongo',
    #         'NAME': 'tradingBot',
    #         'HOST': 'mongodb+srv://bot-trading:YwNpIhTq80ipmCtQ@cluster0.el8nm.mongodb.net/tradingBot?retryWrites=true&w=majority'

    #         'CLIENT': {
    #         },   
    #     }
    # }

DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'tradingBot',
            'CLIENT': {
            'host': 'mongodb+srv://bot-trading:YwNpIhTq80ipmCtQ@cluster0.el8nm.mongodb.net/tradingBot?retryWrites=true&w=majority',
            'username': 'bot-trading',
            'password': 'YwNpIhTq80ipmCtQ' 
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
PROJECT_ROOT   =   os.path.join(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Extra lookup directories for collectstatic to find static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

#  Add configuration for static files storage using whitenoise
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL SERVICE

EMAIL_HOST='smtp.gmail.com'
EMAIL_USE_TLS=env('EMAIL_USE_TLS')
EMAIL_PORT=env('EMAIL_PORT')
EMAIL_HOST_USER=env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD=env('EMAIL_HOST_PASSWORD')


django_heroku.settings(locals()) 