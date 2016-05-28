# -*- coding: utf-8 -*-

from django.shortcuts import render
from rest_framework import generics, filters
import django_filters

from .serializers import ClockItemSerializer
from .models import ClockItem


class ClockItemFilter(filters.FilterSet):
    min_st = django_filters.DateTimeFilter(name='start_time', lookup_type='gte')
    max_st = django_filters.DateTimeFilter(name='start_time', lookup_type='lt')

    class Meta:
        model = ClockItem
        fields = ['min_st', 'max_st', 'date', 'time_cost_min']


class ClockItemList(generics.ListAPIView):
    queryset = ClockItem.objects.all().order_by('-start_time')
    serializer_class = ClockItemSerializer
    filter_fields = ['date']
    filter_class = ClockItemFilter

