# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-12 07:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('palautebot', '0005_auto_20170517_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='source_id',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='source_type',
            field=models.CharField(choices=[('twitter', 'Twitter')], max_length=2048),
        ),
    ]