# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin

from . import views

app_name = 'tms'
urlpatterns = [
    url(r'^clock_items/$', views.ClockItemList.as_view()),
    url(r'^search/$', views.tms_search, name='tms_search'),
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.calendar, name='about'),
    url(r'^project/$', views.project, name='project'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^report/$', views.report, name='report'),
    url(r'^report/week/$', views.week_report, name='week_report'),
    url(r'^report/day/$', views.day_report, name='day_report'),
    url(r'^report/custom/$', views.custom_report, name='custom_report'),
    url(r'^api/v1/week_stats/$', views.week_stats, name='week_stats'),
]
