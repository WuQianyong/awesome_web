#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : urls
# Fatures:
# Author : qianyong
# Time   : 2017-06-22 17:17
# Version: V0.0.1
#

from django.conf.urls import url

from . import views

app_name = 'comments'

urlpatterns = [
    url(r'^comment/post/(?P<post_pk>[0-9]+)/$',views.post_comment,name='post_comment'),
]