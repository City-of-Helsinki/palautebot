import logging

import pytz
import tweepy
from django.conf import settings

from .models import Feedback
from .open311 import Open311Exception, create_ticket
from .utils import check_required_settings

NUM_OF_TWEETS_TO_FETCH = 100

REQUIRED_SETTINGS = (
    'TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET',
    'SEARCH_STRING',
)

logger = logging.getLogger(__name__)


# This method:
#    1. Fetches user's feedback from Twitter
#    2. Saves id, type and timestamp to the db
#    3. Calls parse_tweet and gets formatted tweet data for feedback api
#    4. Calls create_ticket and gets ticket id for feedback object and url for user
#    5. Tries to answer the tweet with text based on whether create_ticket was successful or not
def handle_twitter():
    twitter_api = initialize_twitter()

    try:
        previous_tweet_id = Feedback.objects.filter(
            source=Feedback.SOURCE_TWITTER
        ).latest(
            'source_created_at'
        ).source_id
    except Feedback.DoesNotExist:
        previous_tweet_id = None

    logger.debug('Fetching tweets, previous_tweet_id {}'.format(previous_tweet_id))

    # Queries maximum of RETURN_COUNT latest tweets containing string
    all_tweets = twitter_api.search(
        settings.SEARCH_STRING,
        rpp=NUM_OF_TWEETS_TO_FETCH,
        since_id=previous_tweet_id,
    )
    logger.debug('Got {} tweet(s)'.format(len(all_tweets)))

    timezone = pytz.timezone('Europe/Helsinki')

    for tweet in all_tweets:
        time = timezone.localize(tweet.created_at)
        feedback, created = Feedback.objects.get_or_create(
            source_id=tweet.id,
            source=Feedback.SOURCE_TWITTER,
            defaults={
                'source_created_at': time
            }
        )

        if not created:
            continue

        logger.debug('New twitter feedback from @{}: {}'.format(tweet.user.screen_name, tweet.text))
        new_feedback_data = parse_twitter_data(tweet)

        # post a ticket to open311
        try:
            ticket_data = create_ticket(new_feedback_data)
        except Open311Exception as e:
            logger.error('Could not create a ticket, exception: {}'.format(e))
            text = 'Pahoittelut @%s! Palautteen tallennus epäonnistui' % tweet.user.screen_name
        else:
            text = 'Kiitos @%s! Seuraa etenemistä osoitteessa: %s' % (tweet.user.screen_name, ticket_data['ticket_url'])
            feedback.ticket_id = ticket_data['ticket_id']
            feedback.save()

        # answer to the tweet
        try:
            logger.debug('Sending answer {} to user @{}'.format(text, tweet.user.screen_name))
            twitter_api.update_status(text, in_reply_to_status_id=tweet.id)
        except tweepy.error.TweepError as e:
            logger.error('Something went wrong with answering the tweet, exception: {}'.format(e))


# This function authenticates BOT and initializes twitter_api object
def initialize_twitter():
    check_required_settings(REQUIRED_SETTINGS)

    twitter_auth = tweepy.OAuthHandler(
        settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET
    )
    twitter_auth.set_access_token(
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    twitter_api = tweepy.API(twitter_auth)
    return twitter_api


def parse_name(name_string):
    return name_string.split(' ') if ' ' in name_string else [name_string, None]


# This function creates feedback dictionary
def parse_twitter_data(tweet):
    url = 'https://twitter.com/'
    url = '%s%s/status/%s' % (url, tweet.user.screen_name, tweet.id)
    description_header = 'Palautetta Twitteristä käyttäjältä '
    ticket_dict = {}
    name = parse_name(tweet.user.name)
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
