# -*- coding: utf-8 -*-
from django.test import TestCase
from palautebot.models import Feedback
from django.core.management.base import BaseCommand
from palautebot.management.commands.palautebot import Command
from django.db import connection
import datetime
import instagram
import mock
import pickle
import tweepy


class TestPalautebotTests(TestCase):
    palautebot_cmd = Command()

    def return_true(*args, **kwargs):
        return True

    @mock.patch(
        'palautebot.management.commands.palautebot.Command.answer_to_facebook',
        side_effect=return_true
    )
    @mock.patch(
        'palautebot.management.commands.palautebot.facebook'
    )
    def test_handle_facebook(self, mock_facebook, mock_answer_to_facebook):
        facebook_api = mock_facebook.GraphAPI.return_value
        facebook_api.get_connections.return_value = {
            'data': [{
                'place': {
                    'name': 'Kaupin urheilupuisto',
                    'location': {
                        'city': 'Tampere',
                        'latitude': 61.50838664923,
                        'longitude': 23.811998587433,
                        'zip': '33520',
                        'country': 'Finland',
                        'street': 'Kuntokatu 5'
                    },
                    'id': '165101696882711'
                },
                'from': {
                    'name': 'TEST USER',
                    'id': '10212867422384955'
                },
                'message': '#helpalaute THIS IS MOCK TEST!',
                'id': '371305646605340_376011896134715',
                'created_time': '2017-06-08T06:06:47+0000',
                'picture': 'https://scontent.xx.fbcdn.net/v/t1.0-0/p130x130/18950941_10212939148218053_3752261721521086714_n.jpg?oh=6ae37475e1a06964c68aa55ac31acf1b&oe=599B8C31',
                'permalink_url':
                'https://www.facebook.com/helpalaute/posts/376011896134715'
            }]
        }
        self.assertEqual(
            self.palautebot_cmd.handle_facebook('2017-06-08T06:06:47+0000'),
            [True]
        )

    def mock_initialize_instagram():
        instagram_api = instagram.client.InstagramAPI(
            access_token='access_token_foo',
            client_secret='client_secret_bar'
        )
        return instagram_api

    def mock_tag_recent_media(count=60, max_tag=None, tag_name=''):
        user = instagram.models.User(
            1234,
            full_name='Testi Tunnus',
            username='viljamitesti',
            profile_picture='http://scontent.cdninstagram.com/t51.2885-19/s150x150/18252826_249371388868526_6280353131582717952_a.jpg'
        )
        recent_media = [instagram.models.Media(
            users_in_photo=[],
            comment_count=0,
            link='https://www.haltu.fi',
            filter='Crema',
            caption=instagram.models.Comment(
                created_at=datetime.datetime(2017, 6, 12, 9, 5, 10),
                user=user,
                id='17843910874198179',
                text='#helpalaute Instagram testi'
            ),
            like_count=0,
            id='0000000000000000001_0000000001',
            comments=[],
            images={
                'thumbnail': instagram.models.Image(
                    'http://www.haltu.fi',
                    100,
                    100
                ),
                'low_resolution': instagram.models.Image(
                    'http://www.haltu.fi',
                    100,
                    100
                ),
                'standard_resolution': instagram.models.Image(
                    'http://www.haltu.fi',
                    100,
                    100
                )
            },
            tags=[instagram.models.Tag('helpalaute')],
            likes=[],
            user=user,
            type='image',
            user_has_liked=False,
            created_time=datetime.datetime(2017, 6, 12, 9, 5, 10))]
        next_ = None
        mock_data_from_instagram = (recent_media, next_)
        return mock_data_from_instagram

    @mock.patch(
        'palautebot.management.commands.palautebot.Command.initialize_instagram',
        side_effect=mock_initialize_instagram
    )
    @mock.patch(
        'palautebot.management.commands.palautebot.InstagramAPI.tag_recent_media',
        side_effect=mock_tag_recent_media
    )
    @mock.patch(
        'palautebot.management.commands.palautebot.Command.answer_to_instagram',
        side_effect=return_true
    )
    def test_handle_instagram(
        self,
        mock_init_instagram,
        mock_tag_recent_media,
        mock_answer_to_instagram
    ):
        self.assertEqual(self.palautebot_cmd.handle_instagram(None), [True])

    @mock.patch('palautebot.management.commands.palautebot.Command')
    @mock.patch('palautebot.management.commands.palautebot.Command.answer_to_tweet', side_effect=return_true)
    def test_handle_twitter(self, mock_cmd, mock_answer_to_tweet):
        twitter_api = mock_cmd.initialize_twitter.return_value
        with open('src/palautebot/palautebot/test_utilities/test_data_twitter.py', 'rb') as data:
            twitter_response = pickle.load(data)
            print('##############', twitter_response)
        twitter_api.search.return_value = twitter_response
        self.assertEqual(self.palautebot_cmd.handle_twitter(None), [True])

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
