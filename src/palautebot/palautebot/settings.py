# -*- coding: utf-8 -*-

from django.conf import settings


TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', None)
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', None)
TWITTER_ACCESS_TOKEN = getattr(settings, 'TWITTER_ACCESS_TOKEN', None)
TWITTER_ACCESS_TOKEN_SECRET = getattr(settings, 'TWITTER_ACCESS_TOKEN_SECRET', None)

INSTAGRAM_CLIENT_ID = getattr(settings, 'INSTAGRAM_CLIENT_ID', None)
INSTAGRAM_CLIENT_SECRET = getattr(settings, 'INSTAGRAM_CLIENT_SECRET', None)
INSTAGRAM_REDIRECT_URI = getattr(settings, 'INSTAGRAM_REDIRECT_URI', None)
INSTAGRAM_ACCESS_TOKEN_SCOPE = getattr(settings, 'INSTAGRAM_ACCESS_TOKEN_SCOPE', None)
INSTAGRAM_ACCESS_TOKEN = getattr(settings, 'INSTAGRAM_ACCESS_TOKEN', None)

FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', None)
FACEBOOK_APP_SECRET = getattr(settings, 'FACEBOOK_APP_SECRET', None)
FACEBOOK_PAGE_ID = getattr(settings, 'FACEBOOK_PAGE_ID', None)

HELSINKI_API_KEY = getattr(settings, 'HELSINKI_API_KEY', None)
SEARCH_STRING = getattr(settings, 'SEARCH_STRING', None)
