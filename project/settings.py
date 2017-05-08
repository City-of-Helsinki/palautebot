"""
Django settings for maintenance project.
"""

import os
import dj_database_url

SECRET_KEY = os.environ.get('SECRET_KEY', None)
TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID', None)
TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID', None)
TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID', None)
TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID', None)

BASEDIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = False

ALLOWED_HOSTS = ['*']

LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = (
    'palautebot',

    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'project.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASEDIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
# DATABASE settings are read from env. It should be in form
# postgres://USER:PASSWORD@HOST:PORT/NAME

if os.name == 'nt':
    # Windows
    DEFAULT_DATABASE_URL = 'sqlite:///' + os.path.join(BASEDIR, 'database.db')
else:
    # Linux
    DEFAULT_DATABASE_URL = 'sqlite:////' + os.path.join(BASEDIR, 'database.db')

db_dict = dj_database_url.config(default=DEFAULT_DATABASE_URL)
DATABASES = {
    'default': db_dict,
}


LOCALE_PATHS = (
    os.path.join(BASEDIR, 'locale'),
)

LANGUAGES = (
    ('en', 'English'),
)

USE_I18N = True
USE_L10N = True
USE_TZ = True

TIME_ZONE = 'Europe/Helsinki'

SHORT_DATE_FORMAT = 'd.m.Y'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASEDIR, '..', 'staticroot')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = (os.path.join(BASEDIR, 'static'),)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASEDIR, '..', 'mediaroot')

SSLIFY_DISABLE = True

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

