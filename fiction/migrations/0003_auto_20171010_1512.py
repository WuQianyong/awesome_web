# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-10 07:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fiction', '0002_post_views'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_time']},
        ),
    ]
