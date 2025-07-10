from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost']

SECRET_KEY = 'django-insecure-@l6scf77o1fa%k*+s=lkvpt1+pp)f0q*c(0ozcoba(-ys%bb2v'

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}