import json
import pickle
from copy import deepcopy
from unittest import mock

import pytest
import responses
from tweepy import API, OAuthHandler
from tweepy.models import DirectMessage as TweepyDirectMessage

from feedback.custom_tweepy_api import CustomTweepyAPI, custom_parser
from feedback.tests.data.direct_message_json import new_direct_message_api_response, test_direct_message_json


@pytest.fixture(autouse=True)
def override_settings(settings):
    for setting_name in (
        'TWITTER_CONSUMER_KEY',
        'TWITTER_CONSUMER_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'OPEN311_API_KEY',
        'OPEN311_API_SERVICE_CODE',
    ):
        value = 'test_{}'.format(setting_name)
        setattr(settings, setting_name, value)

    settings.OPEN311_API_BASE_URL = 'http://test_OPEN311_API_BASE_URL'
    settings.OPEN311_FEEDBACK_URL = 'http://test_OPEN311_FEEDBACK_URL?fid={}'
    settings.OPEN311_TICKET_POLLING_TIME = 24*30

    settings.TWITTER_USER_RATE_LIMIT_AMOUNT = 5
    settings.TWITTER_USER_RATE_LIMIT_PERIOD = 60*24
    settings.SEARCH_STRING = '#helpalaute'


@pytest.fixture(scope='session')
def tweepy_search_result():
    with open('feedback/tests/data/pickled_tweepy_search_result', 'rb') as data:
        return pickle.load(data)


@pytest.fixture(scope='session')
def tweepy_user(tweepy_search_result):
    user = deepcopy(tweepy_search_result[0].user)
    setattr(user, 'id', '1234567890')
    return user


@pytest.fixture
def expected_parsed_data():
    return {
        'title': 'Twitter-palaute',
        'description': (
            'Palautetta Twitterissä käyttäjältä ViljamiTesti\n Tämä on testi kahdella kuvalla '
            '\N{TIGER FACE} https://t.co/rjnxqVko2Z\nhttps://twitter.com/ViljamiTesti/status/874885713845735424'
        ),
        'first_name': 'Testi',
        'last_name': 'Tunnus',
        'media_url': 'https://pbs.twimg.com/media/DCQ3t3TW0AEYlqU.jpg',
        'lat': None,
        'long': None,
    }


@pytest.fixture
def tweepy_direct_message():
    test_direct_message = json.loads(test_direct_message_json)
    test_direct_message['text'] = 'https://twitter.com/fooman/status/12345'
    return TweepyDirectMessage.parse(API(), test_direct_message)


@responses.activate
@pytest.fixture
def custom_direct_messages(tweepy_search_result):
    with mock.patch('tweepy.API.get_user', return_value=tweepy_search_result[0].user):
        dm_json = json.loads(new_direct_message_api_response)
        responses.add(responses.GET, 'https://api.twitter.com/1.1/direct_messages/events/list.json',
                      json=dm_json, status=200)

        auth = OAuthHandler('consumer-key', 'consumer-secret')
        auth.set_access_token('access-token', 'access-token-secret')
        return CustomTweepyAPI(auth, parser=custom_parser).direct_messages()
