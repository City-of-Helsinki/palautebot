import pytz
import tweepy
from django.conf import settings

from .feedback_requests import create_ticket
from .models import Feedback

# max num of tweets to fetch
RETURN_COUNT = 100


# This method:
#    1. Fetches user's feedback from Twitter
#    2. Saves id, type, timestamp and ticket_id to the db
#    3. Calls parse_tweet and gets formatted tweet data for feedback api
#    4. Calls create_ticket and gets url for user
#    5. Calls answer_to_tweet that and gets True or False
def handle_twitter():
    try:
        latest_twitter = Feedback.objects.filter(
            source='twitter'
        ).latest('source_created_at')
        previous_tweet_id = latest_twitter.source_id
    except Feedback.DoesNotExist as e:
        previous_tweet_id = None

    # Queries maximum of RETURN_COUNT latest tweets containing string
    twitter_api = initialize_twitter()
    all_tweets = twitter_api.search(
        settings.SEARCH_STRING,
        rpp=RETURN_COUNT,
        since_id=previous_tweet_id,
    )
    success_list_twitter = []
    timezone = pytz.timezone('Europe/Helsinki')
    for tweet in all_tweets:
        time = timezone.localize(tweet.created_at)
        tweet_db_data, created = Feedback.objects.get_or_create(
            source_id=tweet.id,
            source='twitter',
            defaults={
                'ticket_id': 'twitter-ticket-%s' % (tweet.id),
                'source_created_at': time
            }
        )
        if created is False:
            # Record already in db
            success_list_twitter.append(False)
            continue
        else:
            feedback = parse_twitter_data(tweet)
            ticket_url = create_ticket(
                tweet_db_data.source, feedback)
            if ticket_url == '':
                text = 'Pahoittettelut @%s! Palautteen tallennus epäonnistui' % (
                    tweet.user.screen_name)
                success_list_twitter.append(False)
            else:
                text = 'Kiitos @%s! Seuraa etenemistä osoitteessa: %s' % (
                    tweet.user.screen_name, ticket_url
                )
                success_list_twitter.append(True)
            answer_successful = answer_to_tweet(
                twitter_api,
                text,
                tweet.id
            )
            if answer_successful is True:
                print('Tweet %s answered' % (tweet.id))
            else:
                print('something went wrong with answering the tweet')
    else:
        if success_list_twitter == []:
            success_list_twitter.append(False)
    return success_list_twitter


# This function posts an answer to the user's twitter post
def answer_to_tweet(twitter_api, msg, tweet_id):
    tweet_answer = []
    try:
        tweet_answer = twitter_api.update_status(
            msg,
            in_reply_to_status_id=tweet_id
        )
    except tweepy.error.TweepError as e:
        tweet_answered = False
    if tweet_answer != []:
        tweet_answered = True
    else:
        tweet_answered = False
    return tweet_answered


# This function authenticates BOT and initializes twitter_api object
def initialize_twitter():
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


# This function parses the given name
def parse_name(name_string):
    name_list = []
    if ' ' in name_string:
        name_list = name_string.split(' ')
    else:
        name_list.append(name_string)
        name_list.append(None)
    return name_list


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
