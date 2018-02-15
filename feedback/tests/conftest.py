import pickle

import pytest


@pytest.fixture(autouse=True)
def override_settings(settings):
    for setting_name in (
        'TWITTER_CONSUMER_KEY',
        'TWITTER_CONSUMER_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'OPEN311_API_KEY',
        'OPEN311_API_SERVICE_CODE',
        'OPEN311_POST_API_URL',
        'SEARCH_STRING',
    ):
        value = 'test_{}'.format(setting_name)
        if setting_name == 'OPEN311_POST_API_URL':
            value = 'http://{}'.format(value)
        setattr(settings, setting_name, value)

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
