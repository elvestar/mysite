# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals


class Utils(object):
    @staticmethod
    def item_url(item):
        return '/' + item.uri + '/'

    @staticmethod
    def to_date(dt):
        return dt.strftime('%Y-%m-%d')

    @staticmethod
    def to_date_slash(dt):
        return dt.strftime('%Y/%m/%d')

    @staticmethod
    def to_date_short(dt):
        return dt.strftime('%y/%-m/%-d')

    @staticmethod
    def to_datetime(dt):
        return dt.strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def item_date(item):
        return Utils.to_date(item.date)

    @staticmethod
    def item_date_slash(item):
        return Utils.to_date_slash(item.date)

    @staticmethod
    def item_date_short(item):
        return Utils.to_date_short(item.date)

    @staticmethod
    def item_datetime(item):
        if item.time is not None:
            return Utils.to_datetime(item.time)
        else:
            return Utils.item_date(item)
