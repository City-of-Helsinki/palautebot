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
        Feedback.objects.all().delete()

        for result in Feedback.objects.all():
            print(result.ticket_id)
        try:
            latest_facebook = Feedback.objects.filter(
                source_type='facebook'
            ).latest('source_created_at')
            previous_facebook_post_time = latest_facebook.source_created_at
        except Feedback.DoesNotExist as e:
            previous_facebook_post_time = None
        try:
            latest_instagram = Feedback.objects.filter(
                source_type='instagram'
            ).latest('source_created_at')
            previous_instagram_media = latest_instagram.source_id
        except Feedback.DoesNotExist as e:
            previous_instagram_media = None
        try:
            latest_twitter = Feedback.objects.filter(
                source_type='twitter'
            ).latest('source_created_at')
            previous_tweet_id = latest_twitter.source_id
        except Feedback.DoesNotExist as e:
            previous_tweet_id = None

        self.handle_facebook(previous_facebook_post_time)
        self.handle_instagram(max_tag_id=previous_instagram_media)
        self.handle_tweets(previous_tweet_id)

    def answer_to_facebook(self, facebook_api, comment_id, msg):
        facebook_api.put_object(
            parent_object=comment_id,
            connection_name='feed',
            message=msg
        )
        # DOES NOT WORK AT THE MOMENT
        # (needs to be reviewed by fb in order to work.)

    def answer_to_instagram(self, url, media_id, msg):
        msg = '%s %s' % (msg, url)
        instagram_api = self.authenticate_instagram()
        instagram_api.create_media_comment(media_id, msg)
        return

    def answer_to_tweet(self, url, msg, tweet_id):
        twitter_api = self.authenticate_twitter()
        msg = '%s %s' % (msg, url)
        twitter_api.update_status(msg, tweet_id)

    def authenticate_facebook(self):
        # This function constructs facebook_api object 
        # that's used in querying facebook data
        facebook_api = facebook.GraphAPI(
            access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN
        )
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
        feedback['service_code'] = settings.HELSINKI_API_SERVICE_CODE
        print(feedback)
        return True

    def handle_facebook(self, previous_post_time):
        success_list_facebook = []
        facebook_api = self.authenticate_facebook()
        facebook_feed = facebook_api.get_connections(
            settings.FACEBOOK_PAGE_ID,
            'feed',
            fields= 'id, created_time, message, picture, from, permalink_url, place',
            since=previous_post_time
        )
        for post in facebook_feed['data']:
            if 'message' in post:
                if settings.SEARCH_STRING not in post['message']:
                    success_list_facebook.append(False)
                    continue
                else:
                    facebook_db_data, created = Feedback.objects.get_or_create(
                        source_id=post['id'],
                        source_type='facebook',
                        defaults={
                            'ticket_id': 'facebook-ticket-%s' % (post['id']),
                            'source_created_at': post['created_time']
                        }
                    )
                    if created is False:
                        # Record already in db
                        success_list_facebook.append(False)
                        continue
                    else:
                        feedback = self.parse_facebook_data(post, facebook_api)
                        if self.create_ticket(
                            facebook_db_data.source_type,
                            feedback
                        ) is True:
                            message = 'Kiitos! Seuraa etenemistä osoitteessa: '
                            ticket_url = 'seuraapalautettataalla.fi'
                            success_list_facebook.append(True)
                        else:
                            message = 'Palautteen tallennus epäonnistui'
                            success_list_facebook.append(False)
                        # self.answer_to_facebook(facebook_api, post['id'], message)
        return success_list_facebook
    def handle_instagram(
        self,
        max_tag_id,
        search_string=settings.SEARCH_STRING,
        return_count=60
    ):
        # Commenting with api is resticted to 60times/hour
        # Queries max 60 next instagram pictures containing string
        # and starting from max_tag_id
        success_list_instagram = []
        instagram_api = self.authenticate_instagram()
        search_string = search_string.replace('#', '')
        try:
            recent_media, next_ = instagram_api.tag_recent_media(
                count=return_count,
                max_tag_id=max_tag_id,
                tag_name=search_string
            )
        except InstagramAPIError as e:
            LOG.DEBUG('Couldn\'t fetch data from instagram', e)
            if e == '400':
                LOG.info('No new instagram data')
            success_list_instagram.append(False)
            return success_list_instagram
        if 'id' in recent_media[0]:
            for media in recent_media:
                timezone = pytz.timezone('Europe/Helsinki')
                time = timezone.localize(media.created_time)
                instagram_db_data, created = Feedback.objects.get_or_create(
                    source_id=media.id,
                    source_type='instagram',
                    defaults={
                        'ticket_id': 'instagram-ticket-%s' % (media.id),
                        'source_created_at': time
                    }
                )
                if created is False:
                    # Record already in db
                    success_list_instagram.append(False)
                    continue
                else:
                    feedback = self.parse_instagram_data(media)
                    if self.create_ticket(
                        instagram_db_data.source_type,
                        feedback
                    ) is True:
                        message = 'Kiitos! Seuraa etenemistä osoitteessa: '
                        ticket_url = 'seuraapalautettataalla.fi'
                        success_list_instagram.append(True)
                    else:
                        message = 'Palautteen tallennus epäonnistui'
                        success_list_instagram.append(False)
                    # self.answer_to_instagram(ticket_url, media.id, message)
            return success_list_instagram
        return success_list_instagram
    def handle_tweets(
        self,
        previous_tweet_id,
        return_count=100,
        search_string=settings.SEARCH_STRING
    ):
        # Queries maximum of 100 latest tweets containing string
        twitter_api = self.authenticate_twitter()
        all_tweets = twitter_api.search(
            search_string,
            rpp=return_count,
            since_id=previous_tweet_id
        )
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
                continue
            else:
                feedback = self.parse_twitter_data(tweet)
                if(self.create_ticket(tweet_db_data.source_type, feedback)):
                    message = 'Kiitos! Seuraa etenemistä osoitteessa: '
                    ticket_url = 'seuraapalautettataalla.fi'
                else:
                    message = 'Palautteen tallennus epäonnistui'
                # self.answer_to_tweet(ticket_url, message, tweet.id)

    def parse_name(self, name_string):
        name_list = []
        if ' ' in name_string:
            name_list = name_string.split(' ')
        else:
            name_list.append(name_string)
            name_list.append(None)
        return name_list

    def parse_facebook_data(self, comment, facebook_api):
        description_header = 'Feedback via palaute-bot from user '
        ticket_dict = {}
        name = self.parse_name(comment['from']['name'])
        ticket_dict['first_name'] = name[0]
        ticket_dict['last_name'] = name[1]
        ticket_dict['description'] = '%s%s\n %s\nurl: %s' % (
            description_header,
            comment['from']['name'],
            comment['message'],
            comment['permalink_url']
        )
        ticket_dict['title'] = 'Facebook Feedback'
        try:
            ticket_dict['lat'] = comment['place']['location']['latitude']
            ticket_dict['long'] = comment['place']['location']['longitude']
        except KeyError as e:
            ticket_dict['lat'] = None
            ticket_dict['long'] = None
        try:
            ticket_dict['media_url'] = comment['picture']
        except KeyError as e:
            ticket_dict['media_url'] = None
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
        else:
            ticket_dict['media_url'] = None
        return ticket_dict
# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2 
