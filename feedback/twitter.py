import logging
from datetime import timedelta

import pytz
import tweepy
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from .models import Feedback, Tweet
from .open311 import Open311Exception, create_ticket
from .utils import check_required_settings

NUM_OF_TWEETS_TO_FETCH = 100

REQUIRED_SETTINGS = (
    'TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET',
    'SEARCH_STRING',
)

logger = logging.getLogger(__name__)


class TwitterHandler:
    def __init__(self):
        check_required_settings(REQUIRED_SETTINGS)

        twitter_auth = tweepy.OAuthHandler(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET
        )
        twitter_auth.set_access_token(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.twitter_api = tweepy.API(twitter_auth)
        self.timezone = pytz.timezone('Europe/Helsinki')

    def run(self):
        previous_tweet_id = self._get_previous_tweet_id()

        logger.debug('Fetching tweets, previous_tweet_id {}'.format(previous_tweet_id))
        all_tweets = self._get_search_results(previous_tweet_id)
        logger.debug('Got {} tweet(s)'.format(len(all_tweets)))

        for tweet in all_tweets:
            self._handle_tweet(tweet)

    @transaction.atomic
    def _handle_tweet(self, tweet):
        username = tweet.user.screen_name

        new_tweet_obj, created = Tweet.objects.get_or_create(
            source_id=tweet.id_str,
            defaults={
                'source_created_at': self.timezone.localize(tweet.created_at),
                'user_identifier': username
            }
        )
        if not created:
            logger.debug('Got already existing tweet {}'.format(tweet.text))
            return

        if not self._check_rate_limit(username):
            logger.warning(
                'User exceeded feedback post rate limit, user: @{} feedback: {}'.format(username, tweet.text)
            )
            return

        logger.debug('New twitter feedback from @{}: {}'.format(username, tweet.text))
        new_feedback_data = self._parse_twitter_data(tweet)

        ticket_id = self._create_ticket(new_feedback_data)

        if ticket_id:
            new_feedback_obj, created = Feedback.objects.get_or_create(ticket_id=ticket_id)
            new_tweet_obj.feedback = new_feedback_obj
            new_tweet_obj.save()

            if not created:
                logger.debug('Feedback object already existed, ticked_id {}'.format(ticket_id))

            text = 'Kiitos @%s! Seuraa etenemistä osoitteessa: %s' % (username, new_feedback_obj.get_url())
        else:
            text = 'Pahoittelut @%s! Palautteen tallennus epäonnistui' % username

        logger.debug('Sending answer "{}" to user @{}'.format(text, tweet.user.screen_name))
        self._answer_to_tweet(tweet.id, text)

    @staticmethod
    def _get_previous_tweet_id():
        try:
            return Tweet.objects.latest('source_created_at').source_id
        except Tweet.DoesNotExist:
            return None

    @staticmethod
    def _create_ticket(feedback_data):
        try:
            return create_ticket(feedback_data)
        except Open311Exception as e:
            logger.error('Could not create a ticket, exception: {}'.format(e))
            return None

    @staticmethod
    def _parse_name(name_string):
        return name_string.split(' ') if ' ' in name_string else [name_string, None]

    @staticmethod
    def _parse_twitter_data(tweet):
        url = 'https://twitter.com/'
        url = '%s%s/status/%s' % (url, tweet.user.screen_name, tweet.id)
        description_header = 'Palautetta Twitteristä käyttäjältä '
        ticket_dict = {}
        name = TwitterHandler._parse_name(tweet.user.name)
        ticket_dict['first_name'] = name[0]
        ticket_dict['last_name'] = name[1]
        ticket_dict['description'] = '%s%s\n %s\nurl: %s' % (
            description_header,
            tweet.user.screen_name,
            tweet.text,
            url
        )
        ticket_dict['title'] = 'Twitter Feedback'
        if tweet.geo is not None:
            ticket_dict['lat'] = tweet.geo['coordinates'][0]
            ticket_dict['long'] = tweet.geo['coordinates'][1]
        else:
            ticket_dict['lat'] = None
            ticket_dict['long'] = None
        if 'media' in tweet.entities:
            tweet_media = tweet.entities['media']
            ticket_dict['media_url'] = tweet_media[0]['media_url_https']
        else:
            ticket_dict['media_url'] = None
        return ticket_dict

    @staticmethod
    def _check_rate_limit(username):
        if settings.TWITTER_USER_RATE_LIMIT_PERIOD is None or settings.TWITTER_USER_RATE_LIMIT_AMOUNT is None:
            return True

        rate_limit_period_start = now() - timedelta(minutes=settings.TWITTER_USER_RATE_LIMIT_PERIOD)

        feedback_count = Feedback.objects.filter(
            tweet__source_created_at__gte=rate_limit_period_start,
            tweet__user_identifier=username,
        ).count()
        if feedback_count >= settings.TWITTER_USER_RATE_LIMIT_AMOUNT:
            return False

        return True

    def _get_search_results(self, previous_tweet_id=None):
        tweets = self.twitter_api.search(
            settings.SEARCH_STRING,
            rpp=NUM_OF_TWEETS_TO_FETCH,
            since_id=previous_tweet_id,
        )
        return sorted(tweets, key=lambda x: x.created_at)

    def _answer_to_tweet(self, tweet_id, text):
        try:
            self.twitter_api.update_status(text, in_reply_to_status_id=tweet_id)
        except tweepy.error.TweepError as e:
            logger.error('Something went wrong with answering the tweet, exception: {}'.format(e))
