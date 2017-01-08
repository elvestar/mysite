# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


class Utils(object):
    @staticmethod
    def parse_dt_str(dt_str):
        if len(dt_str) == 10:
            return datetime.strptime(dt_str, '%Y-%m-%d')
        else:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_week_id(d):
        iso_year, week, weekday = d.isocalendar()
        return '%sW%s' % (iso_year, week)

    @staticmethod
    def get_month_id(d):
        return '%sM%s' % (d.year, d.month)

