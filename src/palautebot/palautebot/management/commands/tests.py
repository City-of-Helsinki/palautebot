# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from instagram.bind import InstagramAPIError
from instagram.client import InstagramAPI
from palautebot.management.commands import palautebot
from palautebot import settings

import facebook
import tweepy
import time


import pdb
import requests
import requests_mock
import json



class Command(BaseCommand):
    help = 'Palautebot runner management command'

    def handle(self, *args, **options):
        test_count = 2
        if self.check_facebook_api():
            test_count -= 1
        if self.check_instagram_api():
            test_count -= 1
        # if self.check_twitter_api():
        #     test_count -= 1

        # self.check_db_data_saving()
        # self.check_data_parsing()

        if test_count != 0:
            print('App is not working, pls fix')
        else:
            print('App is working correctly')

    def check_facebook_api(self):

        #Facebook api query limiting with since parameter is not working

        print("Facebook api testing...")
        try:
            facebook_api = facebook.GraphAPI(
            access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN
        )
        except NameError as e:
            print('......failed, facebook-sdk not installed. Error: %s' % (e))
            return False
        try:
            facebook_feed = facebook_api.get_object(
            id=settings.FACEBOOK_PAGE_ID,
            fields='feed',
            since='2017-06-06T09:00:00+00:00'
            )
        except facebook.GraphAPIError as e:
            print("......failed, %s" % (e))
            return False
        if 'data' in facebook_feed['feed']:
            print("......successful")
            return True
        else:
            print("......failed, facebook api query returned faulty data")
            return False

    def check_instagram_api(self):

        #Facebook api query limiting with since parameter is not working

        print("Instagram api testing...")
        try:
            instagram_api = InstagramAPI(
                access_token=settings.INSTAGRAM_ACCESS_TOKEN,
                client_secret=settings.INSTAGRAM_CLIENT_SECRET
            )
        except NameError as e:
            print('......failed, instagram not installed. Error: %s' % (e))
            return False
        try:
            recent_media, next_ = instagram_api.tag_recent_media(
                count=1,
                max_tag_id=None,
                tag_name='helpalaute'
            )
        except InstagramAPIError as e:
            if e != '400':
                print('......Couldnt fetch data from instagram', e)
                return False
            else:
                print('......No new instagram data', e)
                return False
            return
        for media in recent_media:
            if hasattr(media, 'id'):
                print("......successful")
                return True
            else:
                print("......failed, instagram api query returned faulty data")
                return False

    def check_twitter_api(self):

        #Facebook api query limiting with since parameter is not working

        print("Twitter api testing...")
        try:
            twitter_auth = tweepy.OAuthHandler(
                settings.TWITTER_CONSUMER_KEY,
                settings.TWITTER_CONSUMER_SECRET
            )
            twitter_auth.set_access_token(
                settings.TWITTER_ACCESS_TOKEN,
                settings.TWITTER_ACCESS_TOKEN_SECRET
            )
            twitter_api = tweepy.API(twitter_auth)
        except NameError as e:
            print('......failed, tweepy not installed. Error: %s' % (e))
            return False
        try:
            all_tweets = twitter_api.search(
                '#helpalaute',
                rpp=1,
                since_id=None
            )
        except tweepy.error.TweepError as e:
            print('......failed, authentication failed: %s' % (e))
            return False
        #tästä puuttuu vielä pala twitter checkiä.
        # for tweet in all_tweets:
        #     pdb.set_trace()



    # def check_facebook_api(self):
    #     print("...instagram api testing...")
    #     instagram_api = InstagramAPI(
    #         access_token=settings.INSTAGRAM_ACCESS_TOKEN,
    #         client_secret=settings.INSTAGRAM_CLIENT_SECRET
    #     )
    #     if instagram_api.access_token == settings.INSTAGRAM_ACCESS_TOKEN:
    #         print("successful")
    #         return True
    #     else:
    #         print("failed")
    #         return False


    # def check_db_data_saving():
    #     response_data_twitter = self.set_twitter_example_data()
    #     m = requests_mock.Mocker()
    #     m.get('https://api.twitter.com', text=u'rairai vastaus' json=response_data_twitter)
    #     requests.get('https://api.twitter.com').text
    #     previous_tweet_id = None
    #     response = palautebot.Command().handle_tweets(previous_tweet_id)
    #     pdb.set_trace()
    #     # if self.setup(m):
    #     #     print('Test passed')
    #     # else:
    #     #     print('Test failed')

    # # def setup(self, m):
    # #     m.get('http://api.twitter.com', text='Mock response 1...2...3..\n\n')
    # #     requests.get('http://api.twitter.com').text
    # #     previous_tweet_id = None
    # #     response = palautebot.Command().handle_tweets(previous_tweet_id)
    # #     pdb.set_trace
    # #     if response:
    # #         repr(response)
    # #         return True
    # #     else:
    # #         return False
    # def check_data_parsing():

    # def set_twitter_example_data(self):
    #     file_object = open("example_twitter_data.txt", "r")
    #     return file_object;


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
