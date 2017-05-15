
# -*- coding: utf-8 -*-
import facebook
import logging
import pdb
import requests
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
        # self.handle_tweets()
        # self.handle_instagram(max_tag_id='1507810671990037057_5419808626')
        self.handle_facebook()

    def answer_to_facebook(self, facebook_api, comment_id, msg):
        facebook_api.put_object(
            parent_object=comment_id,
            connection_name='feed',
            message=msg
        )
        #DOES NOT WORK AT THE MOMENT (needs correct access token?)

    def answer_to_instagram(self, url, media_id, msg):
        msg = '%s %s' % (msg, url)
        instagram_api = self.authenticate_instagram()
        instagram_api.create_media_comment(media_id, msg)
        return

    def answer_to_tweet(self, url, msg, tweet_id):
        twitter_api = self.authenticate_twitter()
        msg = '%s %s' % (msg, url)
        twitter_api.update_status(msg, tweet_id)

    def authenticate_facebook(sélf):
        print('authenticating...')
        token = facebook.GraphAPI().get_app_access_token(
            settings.FACEBOOK_APP_ID,
            settings.FACEBOOK_APP_SECRET
        )
        # assert(isinstance(token, str) or isinstance(token, unicode))
        facebook_api = facebook.GraphAPI(access_token = token)
        return facebook_api

    def authenticate_instagram(self):
        instagram_api = InstagramAPI(
            access_token=settings.INSTAGRAM_ACCESS_TOKEN,
            client_secret=settings.INSTAGRAM_CLIENT_SECRET
        )
        return instagram_api

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

    def create_ticket(self, source_type, feedback):
        feedback['api_key'] = settings.HELSINKI_API_KEY
        feedback['service_code'] = 2809
        print(feedback)
        return True

    def handle_facebook(self):
        facebook_api = self.authenticate_facebook()
        facebook_feed = facebook_api.get_object(
            id=settings.FACEBOOK_PAGE_ID,
            fields='feed'
        )
        for post in facebook_feed['feed']['data']:
            if post['message'].find(settings.SEARCH_STRING) == -1:
                continue
            else:
                try:
                    facebook_db_data = Feedback.objects.create(
                        ticket_id='facebook-ticket-%s' % (post['id']),
                        source_id=post['id'],
                        source_type='facebook',
                        source_data=post['message'])
                except IntegrityError as e:
                    continue

                feedback = self.parse_facebook_data(post, facebook_api)

                if self.create_ticket(facebook_db_data.source_type, feedback) is True:
                    message = 'Kiitos! Seuraa etenemistä osoitteessa: '
                    ticket_url = 'seuraapalautettataalla.fi'
                else:
                    message = 'Palautteen tallennus epäonnistui'
                self.answer_to_facebook(facebook_api, post['id'], message)

        # self.parse_facebook_data
        # self.create_ticket
        # self.answer_to_facebook

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
                instagram_db_data = Feedback.objects.create(
                    ticket_id='instagram-ticket-%s' % (media.id),
                    source_id=media.id,
                    source_type='instagram',
                    source_data=media.caption.text)
            except IntegrityError as e:
                # media already in db
                continue
            feedback = self.parse_instagram_data(media)
            if self.create_ticket(instagram_db_data.source_type, feedback) is True:
                message = 'Kiitos! Seuraa etenemistä osoitteessa: '
                ticket_url = 'seuraapalautettataalla.fi'
            else:
                message = 'Palautteen tallennus epäonnistui'
            self.answer_to_instagram(ticket_url, media.id, message)

    def handle_tweets(
        self,
        return_count=100,
        search_string=settings.SEARCH_STRING
    ):
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

    def parse_name(self, name_string):
        if ' ' in name_string:
            name_list = name_string.split(' ')
        else:
            name_list[0] = name_string
            name_list[1] = None
        return name_list

    def parse_facebook_data(self, comment, facebook_api):
        description_header = 'Feedback via palaute-bot from user '
        userdata = facebook_api.get_object(id=comment['id'], fields='from')
        ticket_dict = {}
        url_to_post = "www.palautteesivoitlukeataalla.fi"
        name = self.parse_name(userdata['from']['name'])
        ticket_dict['first_name'] = name[0]
        ticket_dict['last_name'] = name[1]
        ticket_dict['description'] = '%s%s\n %s\nurl: %s' % (
            description_header,
            userdata['from']['name'],
            comment['message'],
            url_to_post
        )
        ticket_dict['title'] = 'Facebook Feedback'
        # ticket_dict['lat'] =
        # ticket_dict['long'] =
        # ticket_dict['media_url'] =
        return ticket_dict

    def parse_instagram_data(self, media):
        description_header = 'Feedback via palaute-bot from user '
        ticket_dict = {}
        name = self.parse_name(media.user.full_name)
        ticket_dict['first_name'] = name[0]
        ticket_dict['last_name'] = name[1]
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
        return ticket_dict

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2