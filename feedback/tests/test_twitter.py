from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import now
from tweepy import API

from feedback.models import Feedback
from feedback.open311 import Open311Exception
from feedback.twitter import handle_twitter, initialize_twitter, parse_twitter_data


@pytest.mark.parametrize('required_setting', (
    'TWITTER_CONSUMER_KEY',
    'TWITTER_CONSUMER_SECRET',
    'TWITTER_ACCESS_TOKEN',
    'TWITTER_ACCESS_TOKEN_SECRET',
    'SEARCH_STRING',
))
def test_initialize_twitter_required_settings(settings, required_setting):
    setattr(settings, required_setting, '')

    with pytest.raises(ImproperlyConfigured) as e_info:
        initialize_twitter()

    assert str(e_info.value) == 'Setting {} is not set'.format(required_setting)


def test_initialize_twitter_success():
    twitter_api = initialize_twitter()
    assert isinstance(twitter_api, API)


def test_parse_feedback(tweepy_search_result, expected_parsed_data):
    tweet = tweepy_search_result[0]
    parsed_data = parse_twitter_data(tweet)

    assert parsed_data == expected_parsed_data


@mock.patch(
    'feedback.twitter.create_ticket',
    return_value={'ticket_id': '7', 'ticket_url': 'https://www.foobar.fi'}
)
@mock.patch('tweepy.API.update_status')
@pytest.mark.django_db
def test_handle_twitter_success(update_status, create_ticket, tweepy_search_result, expected_parsed_data):
    Feedback.objects.create(
        source=Feedback.SOURCE_TWITTER,
        source_id='777',
        source_created_at=now(),
        ticket_id='abc123',
    )

    with mock.patch('tweepy.API.search', return_value=tweepy_search_result) as search:
        handle_twitter()

        search.assert_called_with('test_SEARCH_STRING', rpp=100, since_id='777')
        create_ticket.assert_called_with(expected_parsed_data)
        update_status.assert_called_with(
            'Kiitos @ViljamiTesti! Seuraa etenemistä osoitteessa: https://www.foobar.fi',
            in_reply_to_status_id=874885713845735424
        )
        new_feedback = Feedback.objects.latest('id')
        assert new_feedback.ticket_id == '7'


@mock.patch(
    'feedback.twitter.create_ticket',
    return_value={'ticket_id': '7', 'ticket_url': 'https://www.foobar.fi'}
)
@mock.patch('tweepy.API.update_status')
@pytest.mark.django_db
def test_handle_twitter_no_tweets(update_status, create_ticket):
    with mock.patch('tweepy.API.search', return_value=[]):
        handle_twitter()

        update_status.assert_not_called()
        create_ticket.assert_not_called()
        assert not Feedback.objects.count()


@mock.patch('feedback.twitter.create_ticket', side_effect=Open311Exception('Boom!'))
@mock.patch('tweepy.API.update_status')
@pytest.mark.django_db
def test_handle_twitter_create_ticket_failure(update_status, create_ticket, tweepy_search_result):
    with mock.patch('tweepy.API.search', return_value=tweepy_search_result) as search:
        handle_twitter()

        search.assert_called_with('test_SEARCH_STRING', rpp=100, since_id=None)
        update_status.assert_called_with(
            'Pahoittelut @ViljamiTesti! Palautteen tallennus epäonnistui',
            in_reply_to_status_id=874885713845735424
        )
        assert Feedback.objects.count() == 1
