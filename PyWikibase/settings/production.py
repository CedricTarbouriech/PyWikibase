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
