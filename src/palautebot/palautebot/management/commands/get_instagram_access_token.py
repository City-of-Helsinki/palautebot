# -*- coding: utf-8 -*-

import logging
import requests

from django.core.management.base import BaseCommand
from instagram.client import InstagramAPI
from palautebot import settings

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Get instagram access token'

    def handle(self, *args, **options):
        client_id = settings.INSTAGRAM_CLIENT_ID
        client_secret = settings.INSTAGRAM_CLIENT_SECRET
        original_redirect_uri = settings.INSTAGRAM_REDIRECT_URI
        raw_scope = settings.INSTAGRAM_ACCESS_TOKEN_SCOPE
        scope = raw_scope.split(' ')
        # For basic, API seems to need to be set explicitly
        if not scope or scope == [""]:
            scope = ["basic"]

        api = InstagramAPI(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=original_redirect_uri
        )
        redirect_uri = api.get_authorize_login_url(scope=scope)
        info_str = 'Visit this page and authorize access in your browser: '
        print '%s%s'(info_str, redirect_uri)

        code = (
            str(
                input('Paste in code in query string after redirect: ').strip()
            )
        )

        # exchange_code_for_access_token has a bug, missing
        # {'Content-Type': 'application/x-www-form-urlencoded'}
        # header
        # access_token = api.exchange_code_for_access_token(code)

        url = u'https://api.instagram.com/oauth/access_token'
        post_data = {
            u'client_id': client_id,
            u'client_secret': client_secret,
            u'code': code,
            u'grant_type': u'authorization_code',
            u'redirect_uri': original_redirect_uri
        }
        response = requests.post(url, data=post_data)
        account_data = response.json()
        print(account_data)
        print('If no errors copy and paste access token to local settings')
# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
