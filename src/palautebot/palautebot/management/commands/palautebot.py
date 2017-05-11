
# -*- coding: utf-8 -*-

import logging
import pdb
import requests
import facebook
import tweepy

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from instagram.bind import InstagramAPIError
from instagram.client import InstagramAPI
from palautebot import settings
from palautebot.models import Feedback

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Palautebot runner management command'

    def handle(self, *args, **options):
        Feedback.objects.all().delete()
        self.handle_tweets()
        self.handle_instagram(max_tag_id='1507810671990037057_5419808626')

    def authenticate_twitter(self):
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

    def authenticate_instagram(self):
        instagram_api = None
        instagram_api = InstagramAPI(
            access_token=settings.INSTAGRAM_ACCESS_TOKEN,
            client_secret=settings.INSTAGRAM_CLIENT_SECRET
        )
        return instagram_api

    def handle_instagram(
        self,
        max_tag_id,
        search_string=settings.SEARCH_STRING,
        return_count=60
    ):
        # Commenting with api is resticted to 60times/hour
        # Queries 60 next instagram pictures containing string
        # and starting from max_tag_id
        instagram_api = self.authenticate_instagram()
        search_string = search_string.replace('#', '')
        pdb.set_trace()
        try:
            # max_tag_id should be the last checked feedback id
            recent_media, next_ = instagram_api.user_recent_media(
                max_tag_id=max_tag_id,
                count=return_count,
                tag_name=search_string
            )
        except InstagramAPIError as e:
            print('Couldnt fetch data from instagram. Error: %s' % (
                e.status_code)
            )
        for media in recent_media:
            try:
                tweet_db_data = Feedback.objects.create(
                    ticket_id='instagram-ticket-%s' % (media.id),
                    source_id=media.id,
                    source_type='instagram',
                    source_data=media.caption.text)
            except IntegrityError as e:
                # media already in db
                continue
            feedback = self.parse_instagram_data(media)
            if self.create_ticket(tweet_db_data.source_type, feedback) is True:
                message = 'Kiitos! Seuraa etenemistä osoitteessa: '
                ticket_url = 'seuraapalautettataalla.fi'
            else:
                message = 'Palautteen tallennus epäonnistui'
            self.answer_to_instagram(ticket_url, media.id, message)

    def handle_tweets(self, return_count=100, search_string=settings.SEARCH_STRING):
        # Queries maximum of 100 latest tweets containing string
        twitter_api = self.authenticate_twitter()
        all_tweets = twitter_api.search(search_string, rpp=return_count)
        for tweet in all_tweets:
            ticket_url = ''
            try:
                tweet_db_data = Feedback.objects.create(
                    ticket_id='twitter-ticket-%s' % (tweet.id),
                    source_id=tweet.id,
                    source_type='twitter',
                    source_data=tweet.text)
            except IntegrityError as e:
                # Tweet already in db
                continue
            feedback = self.parse_twitter_data(tweet)
            if(self.create_ticket(tweet_db_data.source_type, feedback)):
                message = 'Kiitos! Seuraa etenemistä osoitteessa: '
                ticket_url = 'seuraapalautettataalla.fi'
            else:
                message = 'Palautteen tallennus epäonnistui'
            self.answer_to_tweet(ticket_url, message, tweet.id)

    def answer_to_instagram(self, url, media_id, msg):
        msg = '%s %s' % (msg, url)
        instagram_api = self.authenticate_instagram()
        instagram_api.create_media_comment(media_id, msg)
        return

    def answer_to_tweet(self, url, msg, tweet_id):
        twitter_api = self.authenticate_twitter()
        msg = '%s %s' % (msg, url)
        twitter_api.update_status(msg, tweet_id)

    def create_ticket(self, source_type, feedback):
        feedback['api_key'] = settings.HELSINKI_API_KEY
        feedback['service_code'] = 2809
        print(feedback)
        return True

    def parse_instagram_data(self, media):
        description_header = 'Feedback via palaute-bot from user '
        name = media.user.full_name
        ticket_dict = {}
        if ' ' in name:
            name_list = name.split(' ')
            ticket_dict['first_name'] = name_list[0]
            ticket_dict['last_name'] = name_list[1]
        else:
            ticket_dict['first_name'] = name
        ticket_dict['description'] = '%s%s\n %s\nurl: %s' % (
            description_header,
            media.user.username,
            media.caption.text,
            media.link)
        ticket_dict['title'] = 'Instagram Feedback'

        try:
            ticket_dict['lat'] = media.location.point.latitude
            ticket_dict['long'] = media.location.point.latitude
        except AttributeError as e:
            ticket_dict['lat'] = None
            ticket_dict['long'] = None
        ticket_dict['media_url'] = media.get_standard_resolution_url()
        return ticket_dict

    def parse_twitter_data(self, tweet):
        url = 'https://twitter.com/'
        url = '%s%s/%s' % (url, tweet.user.screen_name, tweet.id)
        name = tweet.user.name
        description_header = 'Feedback via palaute-bot from user '
        ticket_dict = {}
        if ' ' in name:
            name_list = name.split(' ')
            ticket_dict['first_name'] = name_list[0]
            ticket_dict['last_name'] = name_list[1]
        else:
            ticket_dict['first_name'] = name

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
        return ticket_dict

    def parse_facebook_data(self, comment):
        # ticket_dict['first_name'] =
        # ticket_dict['last_name'] =
        # ticket_dict['description'] =
        # ticket_dict['title'] =
        # ticket_dict['lat'] =
        # ticket_dict['long'] =
        # ticket_dict['media_url'] =
        # return ticket_dict
        return True
# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
