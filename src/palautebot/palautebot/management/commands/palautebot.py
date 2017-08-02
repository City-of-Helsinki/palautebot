# -*- coding: utf-8 -*-
import json
import logging
import pytz
import requests
import time
import tweepy

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from palautebot import settings
from palautebot.models import Feedback

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Palautebot runner management command'
# This is the main method
    def handle(self, *args, **options):
        for result in Feedback.objects.all():
            print('%s is in the db' % (result.ticket_id))
        try:
            latest_twitter = Feedback.objects.filter(
                source_type='twitter'
            ).latest('source_created_at')
            previous_tweet_id = latest_twitter.source_id
        except Feedback.DoesNotExist as e:
            previous_tweet_id = None
        self.handle_twitter(previous_tweet_id)

# This function posts an answer to the user's twitter post
    def answer_to_tweet(self, twitter_api, msg, tweet_id):
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

# This function sends the feedback to the Helsinki feedback API 
    def create_ticket(self, source_type, feedback):
        feedback['api_key'] = settings.HELSINKI_API_KEY
        feedback['service_code'] = settings.HELSINKI_API_SERVICE_CODE
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response_new_ticket = requests.post(settings.HELSINKI_POST_API_URL,
            data=feedback, headers=headers)
        url_to_feedback = ''
        new_ticket = response_new_ticket.json()
        print(new_ticket)
        for entry in new_ticket:
            if 'code' in entry:
                print('ERROR: ', entry['code'])
                print('info: ', entry['description'])
                return url_to_feedback
            elif 'service_request_id' in entry:
                break
            else:
                print('something wrong with api data')
                print(entry)
                return url_to_feedback
        try:
            new_ticket_id = new_ticket[0]['service_request_id']
            url_to_feedback = 'https://www.hel.fi/helsinki/fi/kaupunki-ja-hallinto/osallistu-ja-vaikuta/palaute/nayta-palaute?fid=%s' % (new_ticket_id)
        except KeyError as e:
            print('New data doesn\'t contain service_request_id %s' % (new_ticket))
        return url_to_feedback

# This function authenticates BOT and initializes twitter_api object
    def initialize_twitter(self):
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

# This method:
#    1. Fetches user's feedback from Twitter
#    2. Saves id, type, timestamp and ticket_id to the heroku postgres db
#    3. Calls parse_tweet and gets formatted tweet data for feedback api
#    4. Calls create_ticket and gets url for user
#    5. Calls answer_to_tweet that and gets True or False
    def handle_twitter(
        self,
        previous_tweet_id,
        return_count=100,
        search_string=settings.SEARCH_STRING
    ):
        # Queries maximum of 100 latest tweets containing string
        twitter_api = self.initialize_twitter()
        all_tweets = twitter_api.search(
            search_string,
            rpp=return_count,
            since_id=previous_tweet_id
        )
        success_list_twitter = []
        for tweet in all_tweets:
            ticket_url = ''
            timezone = pytz.timezone('Europe/Helsinki')
            time = timezone.localize(tweet.created_at)
            tweet_db_data, created = Feedback.objects.get_or_create(
                source_id=tweet.id,
                source_type='twitter',
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
                feedback = self.parse_twitter_data(tweet)
                ticket_url = self.create_ticket(
                    tweet_db_data.source_type, feedback)
                if ticket_url == '':
                    text = 'Pahoittettelut @%s, palautteen tallennus epäonnistui' % (
                        tweet.user.screen_name)
                    success_list_twitter.append(False)
                else:
                    text = 'Kiitos @%s! Seuraa etenemistä osoitteessa: %s' % (
                        tweet.user.screen_name, ticket_url
                    )
                    success_list_twitter.append(True)
                answer_successful = self.answer_to_tweet(
                    twitter_api,
                    text,
                    tweet.id
                )
                if answer_successful == True:
                    print('Tweet %s answered' % (tweet.id)) 
                else:
                    print('something went wrong with answering the tweet')
        else:
            if success_list_twitter == []:
                success_list_twitter.append(False)
        return success_list_twitter

# This function parses the given name
    def parse_name(self, name_string):
        name_list = []
        if ' ' in name_string:
            name_list = name_string.split(' ')
        else:
            name_list.append(name_string)
            name_list.append(None)
        return name_list

# This function creates feedback dictionary
    def parse_twitter_data(self, tweet):
        url = 'https://twitter.com/'
        url = '%s%s/status/%s' % (url, tweet.user.screen_name, tweet.id)
        description_header = 'Feedback via palaute-bot from user '
        ticket_dict = {}
        name = self.parse_name(tweet.user.name)
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

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
