from unittest import mock

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import now
from tweepy import API

from feedback.models import DirectMessage, Feedback, Tweet
from feedback.open311 import Open311Exception
from feedback.tests.utils import SubstringMatcher
from feedback.twitter import TwitterHandler


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
        TwitterHandler()

    assert str(e_info.value) == 'Setting {} is not set'.format(required_setting)


def test_initialize_twitter_success():
    twitter_handler = TwitterHandler()
    assert isinstance(twitter_handler.twitter_api, API)


def test_parse_feedback(tweepy_search_result, expected_parsed_data):
    tweet = tweepy_search_result[0]
    parsed_data = TwitterHandler._parse_twitter_data(tweet)

    assert parsed_data == expected_parsed_data


@mock.patch('feedback.twitter.create_ticket', return_value='7')
@mock.patch('tweepy.API.update_status')
@pytest.mark.django_db
def test_handle_tweets_success(update_status, create_ticket, tweepy_search_result, expected_parsed_data):
    tweet = Tweet.objects.create(source_id='777', source_created_at=now(), user_identifier='fooman')
    Feedback.objects.create(ticket_id='abc123', tweet=tweet)

    with mock.patch('tweepy.API.search', return_value=tweepy_search_result) as search:
        twitter_handler = TwitterHandler()
        twitter_handler.handle_tweets()

        search.assert_called_with(settings.SEARCH_STRING, rpp=100, since_id='777')
        create_ticket.assert_called_with(expected_parsed_data)
        update_status.assert_called_with(
            'Kiitos @ViljamiTesti! Seuraa etenemistä osoitteessa: http://test_OPEN311_FEEDBACK_URL?fid=7',
            in_reply_to_status_id='874885713845735424'
        )

        new_feedback = Feedback.objects.latest('id')
        assert new_feedback.ticket_id == '7'

        new_tweet = Tweet.objects.latest('id')
        assert new_tweet.user_identifier == 'ViljamiTesti'
        assert new_feedback.tweet == new_tweet


@mock.patch('feedback.twitter.create_ticket', return_value='7')
@mock.patch('tweepy.API.update_status')
@pytest.mark.django_db
def test_handle_tweets_no_tweets(update_status, create_ticket):
    with mock.patch('tweepy.API.search', return_value=[]):
        twitter_handler = TwitterHandler()
        twitter_handler.handle_tweets()

        update_status.assert_not_called()
        create_ticket.assert_not_called()
        assert not Feedback.objects.count()
        assert not Tweet.objects.count()


@mock.patch('feedback.twitter.create_ticket', side_effect=Open311Exception('Boom!'))
@mock.patch('tweepy.API.update_status')
@pytest.mark.django_db
def test_handle_tweets_create_ticket_failure(update_status, create_ticket, tweepy_search_result):
    with mock.patch('tweepy.API.search', return_value=tweepy_search_result) as search:
        twitter_handler = TwitterHandler()
        twitter_handler.handle_tweets()

        search.assert_called_with(settings.SEARCH_STRING, rpp=100, since_id=None)
        update_status.assert_called_with(
            'Pahoittelut @ViljamiTesti! Palautteen tallennus epäonnistui',
            in_reply_to_status_id='874885713845735424'
        )
        assert not Feedback.objects.count()
        assert Tweet.objects.count() == 1


@mock.patch('feedback.twitter.create_ticket')
@mock.patch('tweepy.API.update_status')
@mock.patch('feedback.twitter.logger.warning')
@pytest.mark.django_db
def test_handle_tweets_rate_limit_exceeded(warning, update_status, create_ticket, tweepy_search_result, settings):
    settings.TWITTER_USER_RATE_LIMIT_AMOUNT = 1
    settings.TWITTER_USER_RATE_LIMIT_PERIOD = 60*24*365*100  # "forever"

    tweet = Tweet.objects.create(source_id='777', source_created_at=now(), user_identifier='ViljamiTesti')
    Feedback.objects.create(ticket_id='abc123', tweet=tweet)

    with mock.patch('tweepy.API.search', return_value=tweepy_search_result):
        twitter_handler = TwitterHandler()
        twitter_handler.handle_tweets()

        warning.assert_called_with(SubstringMatcher('User exceeded feedback post rate limit'))
        update_status.assert_not_called()
        create_ticket.assert_not_called()
        assert Feedback.objects.count() == 1
        assert Tweet.objects.count() == 2


@mock.patch('feedback.twitter.TwitterHandler._fetch_single_tweet', return_value='iamatweet')
@mock.patch('feedback.twitter.TwitterHandler._handle_tweet')
@pytest.mark.django_db
def test_handle_direct_messages_success(handle_tweet, fetch_single_tweet, tweepy_direct_message):
    direct_message = DirectMessage.objects.create(source_id='888', source_created_at=now())

    with mock.patch(
            'feedback.twitter.TwitterHandler._fetch_direct_messages',
            return_value=[tweepy_direct_message]) as fetch_direct_messages:
        twitter_handler = TwitterHandler()
        twitter_handler.handle_direct_messages()

        fetch_direct_messages.assert_called_with(direct_message.source_id)
        handle_tweet.assert_called_with('iamatweet', self_submitted=False)
        assert DirectMessage.objects.count() == 2
        assert DirectMessage.objects.latest('id').source_id == tweepy_direct_message.id_str
