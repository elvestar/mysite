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

    @staticmethod
    def min_to_hour(time_min, precision=1):
        return round(float(time_min) / 60.0, precision)

    @staticmethod
    def min_to_hour2(time_min):
        if (time_min % 60) < 10:
            minutes_str = '0' + str(time_min % 60)
        else:
            minutes_str = str(time_min % 60)
        return '%d:%s' % (time_min / 60, minutes_str)
