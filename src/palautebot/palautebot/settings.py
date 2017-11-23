# -*- coding: utf-8 -*-

from django.conf import settings

HELSINKI_API_KEY = getattr(settings, 'HELSINKI_API_KEY', None)
HELSINKI_API_SERVICE_CODE = getattr(settings, 'HELSINKI_API_SERVICE_CODE', None)
HELSINKI_POST_API_URL = getattr(settings, 'HELSINKI_POST_API_URL', None)

SEARCH_STRING = getattr(settings, 'SEARCH_STRING', None)

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', None)
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', None)
TWITTER_ACCESS_TOKEN = getattr(settings, 'TWITTER_ACCESS_TOKEN', None)
TWITTER_ACCESS_TOKEN_SECRET = getattr(settings, 'TWITTER_ACCESS_TOKEN_SECRET', None)
