# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^clock_items/$', views.ClockItemList.as_view()),
    ]
