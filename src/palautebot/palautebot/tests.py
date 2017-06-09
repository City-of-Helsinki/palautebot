# -*- coding: utf-8 -*-
from django.test import TestCase
from palautebot.models import Feedback
from django.core.management.base import BaseCommand
from palautebot.management.commands.palautebot import Command
import mock
import pdb

class TestPalautebotTests(TestCase):
    palautebot_cmd = Command()

    @mock.patch('palautebot.management.commands.palautebot.facebook')
    def test_handle_facebook(self, palautebot_facebook):
        facebook_api = palautebot_facebook.GraphAPI.return_value
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
                'permalink_url': 'https://www.facebook.com/helpalaute/posts/376011896134715'
            }]
        }
        success_list = self.palautebot_cmd.handle_facebook('2017-06-08T06:06:47+0000')
        self.assertEqual(success_list, [True])

    def test_handle_instagram(self, palautebot_instagram):
        instagram_api = palautebot_instagram.InstagramAPI.return_value
        instagram_api.tag_recent_media.return_value = [{
            'images': {
                'thumbnail': Image: https: //scontent.cdninstagram.com/t51.2885-15/s150x150/e35/18809011_461182420885447_6818515699162415104_n.jpg, 
                    'standard_resolution': Image: https: //scontent.cdninstagram.com/t51.2885-15/s640x640/sh0.08/e35/18809011_461182420885447_6818515699162415104_n.jpg, 
                    'low_resolution': Image: https: //scontent.cdninstagram.com/t51.2885-15/s320x320/e35/18809011_461182420885447_6818515699162415104_n.jpg
            },
            'user_has_liked': False,
            'comments': [],
            'like_count': 0,
            'link': 'https://www.instagram.com/p/BUtzVS6AUva/',
            'type': 'image',
            'created_time': datetime.datetime(2017, 5, 30, 11, 58, 30),
            'id': '1526101612530060250_5419808626',
            'user': User: viljamitesti,
            'comment_count': 0,
            'caption': Comment: viljamitesti said "#helpalaute testipalautetta instagramista",
            'filter': 'Gingham',
            'tags': [Tag: helpalaute],
            'users_in_photo': [],
            'likes': []
        }]
        success_list = self.palautebot_cmd.handle_instagram(None, search_string='#helpalaute')
        self.assertEqual(success_list, [True])