#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : urls
# Fatures:
# Author : qianyong
# Time   : 2017/10/10 10:25
# Version: V0.0.1
#


from django.conf.urls import url



from . import views

app_name = 'fiction'
urlpatterns = [
    url(r'^fiction/$', views.FictionView.as_view(), name='fiction'),
    url(r'^$', views.index, name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchivesView.as_view(), name='archives'),
    # url(r'^change/(?P<company_name>\S+)/(?P<info>\S+)/(?P<type>\S+)/(?P<page>[0-9]+)/$', change_info,
    #     name='change_info'),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^tag/(?P<pk>[0-9]+)/$',views.TagView.as_view(),name='tag'),
    # url(r'^all/rss/$',AllPostsRssFeed(),name='rss'),
    url(r'^search/$',views.search,name='search'),
]
