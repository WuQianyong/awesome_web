#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : forms.py
# Fatures:
# Author : qianyong
# Time   : 2017-06-22 16:59
# Version: V0.0.1
#

from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'url', 'text']
