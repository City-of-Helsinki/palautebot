import json
import pickle

import pytest
from tweepy import API
from tweepy.models import DirectMessage as TweepyDirectMessage

from feedback.tests.data.direct_message_json import test_direct_message_json


@pytest.fixture(autouse=True)
def override_settings(settings):
    for setting_name in (
        'TWITTER_CONSUMER_KEY',
        'TWITTER_CONSUMER_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'OPEN311_API_KEY',
        'OPEN311_API_SERVICE_CODE',
        'SEARCH_STRING',
    ):
        value = 'test_{}'.format(setting_name)
        setattr(settings, setting_name, value)

    settings.OPEN311_API_BASE_URL = 'http://test_OPEN311_API_BASE_URL'
    settings.OPEN311_FEEDBACK_URL = 'http://test_OPEN311_FEEDBACK_URL?fid={}'
    settings.OPEN311_TICKET_POLLING_TIME = 24*30

    settings.TWITTER_USER_RATE_LIMIT_AMOUNT = 5
    settings.TWITTER_USER_RATE_LIMIT_PERIOD = 60*24


@pytest.fixture(scope='session')
def tweepy_search_result():
    with open('feedback/tests/data/pickled_tweepy_search_result', 'rb') as data:
        return pickle.load(data)


@pytest.fixture
def expected_parsed_data():
    return {
        'title': 'Twitter Feedback',
        'description': (
            'Palautetta Twitteristä käyttäjältä ViljamiTesti\n #helpalaute Tämä on testi kahdella kuvalla '
            '\N{TIGER FACE} https://t.co/rjnxqVko2Z\nurl: https://twitter.com/ViljamiTesti/status/874885713845735424'
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
