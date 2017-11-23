"""
WSGI config for palautebot project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path[0:0] = [
    './src/palautebot'
]

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise


application = get_wsgi_application()

# static files are served with whitenoise
# see more: https://devcenter.heroku.com/articles/django-assets
application = DjangoWhiteNoise(application) # serve static files

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

