#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include
from gras.shortcut import init_urls

urlpatterns = init_urls('blog')
