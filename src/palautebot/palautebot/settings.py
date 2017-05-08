# -*- coding: utf-8 -*-

from django.conf import settings


TWITTER_CLIENT_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', None)
TWITTER_CLIENT_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', None)
TWITTER_ACCESS_TOKEN = getattr(settings, 'TWITTER_ACCESS_TOKEN', None)
TWITTER_ACCESS_TOKEN_SECRET = getattr(settings, 'TWITTER_ACCESS_TOKEN_SECRET', None)