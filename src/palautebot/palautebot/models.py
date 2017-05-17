
# -*- coding: utf-8 -*-

import logging
from django.db import models
from palautebot import settings


LOG = logging.getLogger(__name__)


class Feedback(models.Model):
    SOURCE_TYPE_TWITTER = 'twitter'
    SOURCE_TYPE_INSTAGRAM = 'instagram'
    SOURCE_TYPE_FACEBOOK = 'facebook'

    SOURCE_TYPE_CHOICES = (
        (SOURCE_TYPE_TWITTER, 'Twitter'),
        (SOURCE_TYPE_INSTAGRAM, 'Facebook'),
        (SOURCE_TYPE_FACEBOOK, 'Facebook'),
    )

    ticket_id = models.CharField(max_length=2048)
    source_id = models.CharField(max_length=2048, unique=True)
    source_type = models.CharField(max_length=2048, choices=SOURCE_TYPE_CHOICES)
    source_created_at = models.DateTimeField(default='2017-05-17T09:00:00+0000')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2