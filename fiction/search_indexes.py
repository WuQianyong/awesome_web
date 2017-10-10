#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : search_indexs
# Fatures:
# Author : qianyong
# Time   : 2017/8/19 16:46
# Version: V0.0.1
#

from haystack import indexes
from .models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()