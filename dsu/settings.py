"""
Django settings for dsu project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path
import pymysql

pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '192.168.0.130', '192.168.0.132', 'dsup-voting-portal.herokuapp.com', '127.0.0.1', 'dsup.herokuapp.com', 'localhost:8000',
                 'dsu-front.herokuapp.com', 'dsu-front.herokuapp.com:8000', 'dsu-front.herokuapp.com:8080', 'dsu-front.herokuapp.com:', 'claim-your-seat.herokuapp.com']

# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'vote.apps.VoteConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    # 'drf_spectacular',
    'live.apps.LiveConfig',
    'bills.apps.BillsConfig',
    # 'django_extensions',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'dsu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'dsu.wsgi.application'
ASGI_APPLICATION = "dsu.asgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

import json
if not json.loads(os.environ.get('PRODUCTION').lower()):
    # production
    print("running in dev. using sqlit3 and channels in memory layer")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }

else:
    print("runnig the app in production with main database")
    DATABASES = {
        'default': {
                'ENGINE': os.environ.get('DB_ENGINE'),
                'NAME':  os.environ.get('DB_NAME'),
                'USER': os.environ.get('DB_USER'),
                'PASSWORD': os.environ.get('DB_PASSWORD'),
                'HOST': os.environ.get('DB_HOST'),
                'PORT': os.environ.get('DB_PORT'),
                'OPTIONS': {
                'init_command': 'SET sql_mode="STRICT_TRANS_TABLES"',
                }
            }
        }

    print("REDIS_URL: ",os.environ.get('REDIS_URL'))
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [os.environ.get('REDIS_URL')],
            },
            # "ROUTING": "chat.routing.channel_routing",
        },
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

STATIC_URL = '/static/'  # / added by siva

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL_BACKEND       = os.environ.get('EMAIL_BACKEND')
# EMAIL_HOST          = os.environ.get('EMAIL_HOST')
# EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# EMAIL_PORT          = os.environ.get('EMAIL_PORT')
# EMAIL_USE_TLS       = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ceewa30@gmail.com'
EMAIL_HOST_PASSWORD = 'lphxoimlvsuwhynz'


REST_FRAMEWORK = {
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}


from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
}

# this is for  the backend jwt auth.
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
CORS_ALLOW_ALL_ORIGINS = True # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']
CORS_ORIGIN_WHITELIST = ['http://localhost:8080', 'http://localhost',
                         'https://dsu-front.herokuapp.com', 'http://dsu-front.herokuapp.com',
                         'http://claim-your-seat.herokuapp.com', 'https://claim-your-seat.herokuapp.com']

CSRF_TRUSTED_ORIGINS = ['http://dsup-voting-portal.herokuapp.com',
                        'https://dsup-voting-portal.herokuapp.com',
                        'https://dsu-front.herokuapp.com',
                        'http://dsu-front.herokuapp.com',
                        'http://claim-your-seat.herokuapp.com'
                        'https://claim-your-seat.herokuapp.com']
