# -*- coding: utf-8 -*-

from rest_framework import serializers

from .models import ClockItem


class ClockItemSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = []
        model = ClockItem
