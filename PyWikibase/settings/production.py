from .base import *

import environ

env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', 'pecunia-app.huma-num.fr']

SECRET_KEY = env('SECRET_KEY')
DATABASES = {'default':
                 {'ENGINE': 'django.db.backends.postgresql_psycopg2',
                  'NAME': env('DATABASE_NAME'),
                  'USER': env('DATABASE_USER'),
                  'PASSWORD': env('DATABASE_PASS'),
                  }
             }

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True