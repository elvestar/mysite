# -*- coding: utf-8 -*-
from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

from . import views

schema_view = get_swagger_view(title='TMS API')

app_name = 'tms'
urlpatterns = [
    url(r'^clock_items/$', views.ClockItemList.as_view()),
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.calendar, name='about'),

    url(r'^project/$', views.get_project, name='project'),
    url(r'^project/analyzer/$', views.time_analyzer, name='time_analyzer'),
    url(r'^project/all/$', views.all_projects, name='all_projects'),

    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^report/$', views.get_report, name='report'),
    url(r'^report/week/$', views.week_report, name='week_report'),
    url(r'^report/day/$', views.day_report, name='day_report'),
    url(r'^report/year/$', views.year_report, name='year_report'),
    url(r'^report/custom/$', views.custom_report, name='custom_report'),

    url(r'^api/docs/$', schema_view, name='api_docs'),
    url(r'^api/v1/clock_items/$', views.ClockItemList.as_view()),
    url(r'^api/v1/week_stats/$', views.api_week_stats),
    url(r'^api/v1/day_stats/$', views.api_day_stats),
    url(r'^api/v1/project_stats/$', views.api_project_stats),
    url(r'^api/v1/week_stats_old/$', views.week_stats, name='week_stats'),
    url(r'^api/v1/year_stats_step_by_month_and_week/$', views.year_stats_step_by_month_and_week,
        name='year_stats_step_by_month_and_week'),
]
