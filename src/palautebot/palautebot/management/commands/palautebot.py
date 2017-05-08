
# -*- coding: utf-8 -*-

import logging
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from palautebot.models import Feedback
from palautebot import settings

import tweepy

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Palautebot runner management command'

    def handle(self, *args, **options):
        self.handle_tweets()

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


    def handle_tweets(self, return_count=100, search_string='#TestiPalaute'):
        api = self.authenticate_twitter()
        all_tweets = api.search(search_string, rpp=return_count)
        for tweet in all_tweets:
            ticket_url = ''
            try:
                ticket = Feedback.objects.create(
                    ticket_id="twitter-ticket-%s" % (tweet.id),
                    source_id=tweet.id,
                    source_type="twitter",
                    source_data=tweet.text)
            except IntegrityError as e:
                #Tweet already in db
                continue

            if(self.create_ticket(ticket.ticket_id, tweet) is True):
                message = "Kiitos! Seuraa etenemistä osoitteessa: "
                ticket_url = "seuraapalautettataalla.fi"
            else:
                message = "Palautteen tallennus epäonnistui"
            #self.answer_to_tweet(ticket_url, message, tweet.id)
            print('Answer to tweet called..')

    def answer_to_tweet(self, url, msg, tweet_id):
        api = self.authenticate_twitter()
        msg = "%s %s" % (msg, url)
        api.update_status(msg, tweet_id)

    def create_ticket(self, ticket_id, feedback_object):
        # TICKET INFO
        # TWEET INFO
        # api_key = "from helsinki?"
        # service_object_id = "required field if no coordinates in the tweet)"
        # service_code = "required field 'The unique identifier for the service request type'"
        # title = tweet_object.text
        # description = "required field 10 to 5000 characters--- must parse smth here."
        # tweet_id = tweet_object.id
        # username = tweet_object.user.screen_name
        # url = "%s%s/%s" % (url, username, tweet_object.id)
        # media_url = list()
        return True

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
