import logging
import re
from datetime import timedelta

import pytz
import tweepy
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from .models import DirectMessage, Feedback, Tweet
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
        self.handle_tweets()
        self.handle_direct_messages()

    def handle_tweets(self):
        latest_tweet_id = Tweet.objects.get_latest_source_id()

        logger.debug('Fetching tweets, latest_tweet_id {}'.format(latest_tweet_id))
        tweets = self._fetch_tweets(latest_tweet_id)
        logger.debug('Fetched {} tweet(s)'. format(len(tweets)))

        for tweet in tweets:
            self._handle_tweet(tweet)

    def handle_direct_messages(self):
        latest_direct_message_id = DirectMessage.objects.get_latest_source_id()

        logger.debug('Fetching direct messages, latest_tweet_id {}'.format(latest_direct_message_id))
        direct_messages = self._fetch_direct_messages(latest_direct_message_id)
        logger.debug('Fetched {} direct message(s)'.format(len(direct_messages)))

        for direct_message in direct_messages:
            self._handle_direct_message(direct_message)

    @transaction.atomic
    def _handle_tweet(self, tweet, self_submitted=True):
        username = tweet.user.screen_name
        logger.debug(
            'Handling a tweet from @{}: "{}" ({})'.format(username, tweet.text, tweet.id_str)
        )

        new_tweet_obj, created = Tweet.objects.get_or_create(
            source_id=tweet.id_str,
            defaults={
                'source_created_at': self.timezone.localize(tweet.created_at),
                'user_identifier': username
            }
        )
        if not created:
            logger.warning('Already existing tweet "{}" ({})'.format(tweet.text, tweet.id_str))
            return

        if hasattr(tweet, 'retweeted_status'):
            logger.debug('The tweet is a retweet, skipping')
            return

        if not self._check_rate_limit(username):
            logger.warning(
                'User exceeded feedback post rate limit, user: @{} feedback: "{}" ({})'.format(
                    username, tweet.text, tweet.id_str
                )
            )
            return

        logger.info(
            'New {} submitted feedback from @{}: "{}" ({})'.format(
                'self' if self_submitted else 'third party', username, tweet.text, tweet.id_str))
        new_feedback_data = self._parse_twitter_data(tweet)

        ticket_id = self._create_ticket(new_feedback_data)
        feedback_url = None

        if ticket_id:
            new_feedback_obj, created = Feedback.objects.get_or_create(ticket_id=ticket_id, tweet=new_tweet_obj)
            feedback_url = new_feedback_obj.get_url()

        answer_text = self._get_feedback_answer_text(bool(ticket_id), username, feedback_url, self_submitted)

        if answer_text is not None:
            self.answer_to_tweet(tweet.id_str, answer_text)

    @transaction.atomic
    def _handle_direct_message(self, direct_message):
        username = direct_message.sender.screen_name
        logger.debug(
            'Handling a direct message from @{}: "{}" ({})'.format(username, direct_message.text, direct_message.id_str)
        )

        new_direct_message_obj, created = DirectMessage.objects.get_or_create(
            source_id=direct_message.id_str,
            defaults={
                'source_created_at': self.timezone.localize(direct_message.created_at),
            }
        )
        if not created:
            logger.warning(
                'Already existing direct message "{}" ({})'.format(direct_message.text, direct_message.id_str)
            )
            return

        status_id = self._parse_status_id_from_direct_message(direct_message)
        if not status_id:
            logger.debug('The message does not seem to be a redirected feedback, skipping')
            return

        logger.debug('The message contains a feedback link, fetching the original tweet {}'.format(status_id))

        original_tweet = self._fetch_single_tweet(status_id)
        if original_tweet:
            logger.info('@{} submitted tweet {} as feedback'.format(username, status_id))
            self._handle_tweet(original_tweet, self_submitted=False)

    def _fetch_tweets(self, latest_tweet_id=None):
        try:
            tweets = self.twitter_api.search(
                settings.SEARCH_STRING,
                rpp=NUM_OF_TWEETS_TO_FETCH,
                since_id=latest_tweet_id,
            )
            return sorted(tweets, key=lambda x: x.created_at)
        except tweepy.error.TweepError as e:
            logger.error('Cannot fetch search results, exception: {}'.format(e))
            return []

    def _fetch_direct_messages(self, latest_direct_message_id=None):
        try:
            return self.twitter_api.direct_messages(since_id=latest_direct_message_id)
        except tweepy.error.TweepError as e:
            logger.error('Cannot fetch direct messages, exception: {}'.format(e))

    def _fetch_single_tweet(self, status_id):
        try:
            return self.twitter_api.get_status(status_id)
        except tweepy.error.TweepError as e:
            logger.error('Cannot fetch tweet with ID {}, exception: {}'.format(status_id, e))
            return None

    def answer_to_tweet(self, tweet_id, text):
        logger.debug('Sending answer "{}" to tweet {}'.format(text, tweet_id))
        try:
            self.twitter_api.update_status(text, in_reply_to_status_id=tweet_id)
        except tweepy.error.TweepError as e:
            logger.error('Something went wrong with answering the tweet, exception: {}'.format(e))

    @staticmethod
    def _get_feedback_answer_text(success, username, feedback_url, self_submitted):
        if success:
            if self_submitted:
                return 'Kiitos @{}! Seuraa etenemistä osoitteessa: {}'.format(username, feedback_url)
            else:
                return ('Hei @{}! Olen Helsingin kaupungin palautebotti. '
                        'Välitin viestisi kaupungin asiantuntijalle ja siihen vastataan muutaman päivän kuluessa. '
                        'Seuraa etenemistä osoitteesta: {}').format(username, feedback_url)
        elif self_submitted:
            return 'Pahoittelut @{}! Palautteen tallennus epäonnistui'.format(username)

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
        description_header = 'Palautetta Twitterissä käyttäjältä '
        ticket_dict = {}
        name = TwitterHandler._parse_name(tweet.user.name)
        ticket_dict['first_name'] = name[0]
        ticket_dict['last_name'] = name[1]
        ticket_dict['description'] = '%s%s\n%s\n%s' % (
            description_header,
            tweet.user.screen_name,
            tweet.text.replace(settings.SEARCH_STRING, ''),
            url
        )
        ticket_dict['title'] = 'Twitter-palaute'
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

    @staticmethod
    def _parse_status_id_from_direct_message(direct_message):
        try:
            url = direct_message.entities['urls'][0]['expanded_url']
        except (KeyError, IndexError):
            return None
        match = re.match(r'https?://twitter.com/[a-zA-Z0-9]+/status/([0-9]*)', url)
        return match.group(1) if match else None
