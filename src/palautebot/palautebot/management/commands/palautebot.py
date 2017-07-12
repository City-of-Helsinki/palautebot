# -*- coding: utf-8 -*-
import facebook
import logging
import pytz
import requests
import time
import tweepy

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from instagram.bind import InstagramAPIError
from instagram.client import InstagramAPI
from palautebot import settings
from palautebot.models import Feedback

import pdb

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Palautebot runner management command'

    def handle(self, *args, **options):
        # Feedback.objects.all().delete()

        for result in Feedback.objects.all():
            print('%s is in the db' % (result.ticket_id))
        try:
            latest_facebook = Feedback.objects.filter(
                source_type='facebook'
            ).latest('source_created_at')
            previous_facebook_post_time = latest_facebook.source_created_at
        except Feedback.DoesNotExist as e:
            previous_facebook_post_time = None
        self.handle_twitter(previous_tweet_id)

    def answer_to_tweet(self, twitter_api, url, msg, tweet_id):
        msg = '%s %s' % (msg, url)
        tweet_answer = []
        # try:
        #     tweet_answer = twitter_api.update_status(
        #         msg,
        #         in_reply_to_status_id=tweet_id
        #     )
        # except tweepy.error.TweepError as e:
        #     tweet_answered = False
        # if tweet_answer != []:
        #     tweet_answered = True
        # else:
        #     tweet_answered = False
        # return tweet_answered
        return True

    def create_ticket(self, source_type, feedback):
        feedback['api_key'] = settings.HELSINKI_API_KEY
        feedback['service_code'] = settings.HELSINKI_API_SERVICE_CODE
        print(feedback)
        return True

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
                if self.create_ticket(tweet_db_data.source_type, feedback):
                    text = 'Kiitos @%s! Seuraa etenemistä osoitteessa: ' % (
                        tweet.user.screen_name
                    )
                    ticket_url = 'seuraapalautettataalla.fi'
                    success_list_twitter.append(True)
                else:
                    text = 'Palautteen tallennus epäonnistui'
                    success_list_twitter.append(False)
                answer_successful = self.answer_to_tweet(
                    twitter_api,
                    ticket_url,
                    text,
                    tweet.id
                )
        else:
            if success_list_twitter == []:
                success_list_twitter.append(False)
        return success_list_twitter

    def parse_name(self, name_string):
        name_list = []
        if ' ' in name_string:
            name_list = name_string.split(' ')
        else:
            name_list.append(name_string)
            name_list.append(None)
        return name_list

    def parse_twitter_data(self, tweet):
        url = 'https://twitter.com/'
        url = '%s%s/%s' % (url, tweet.user.screen_name, tweet.id)
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
