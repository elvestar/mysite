# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals


WEEK_DAY_STR = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


class ItemUtils(object):
    @staticmethod
    def item_url(item):
        return '/' + item.uri

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
    def to_weekday_ch(dt):
        return WEEK_DAY_STR[int(dt.strftime('%w'))]

    @staticmethod
    def timedelta_min(dt1, dt2):
        return (dt2 - dt1).seconds / 60

    @staticmethod
    def item_date(item):
        return ItemUtils.to_date(item.date)

    @staticmethod
    def item_date_slash(item):
        return ItemUtils.to_date_slash(item.date)

    @staticmethod
    def item_date_short(item):
        return ItemUtils.to_date_short(item.date)

    @staticmethod
    def item_datetime(item):
        if item.time is not None:
            return ItemUtils.to_datetime(item.time)
        else:
            return ItemUtils.item_date(item)

    @staticmethod
    def is_xxx_item(item, category):
        if item.uri.startswith(category + '/'):
            return True

    @staticmethod
    def is_life_item(item):
        return ItemUtils.is_xxx_item(item, 'life')

    @staticmethod
    def is_blog_item(item):
        return ItemUtils.is_xxx_item(item, 'blog')

    @staticmethod
    def is_note_item(item):
        return ItemUtils.is_xxx_item(item, 'notes')


class Utils(object):
    @staticmethod
    def parse_exif_info(exif_info):
        pass
        # Parse gps info
        gps_info = exif_info[34853]
        longitude = gps_info[4]
        longitude = float(longitude[0][0]) / float(longitude[0][1]) + \
                    (float(longitude[1][0]) / float(longitude[1][1])) / 60.0
        if gps_info[3] == 'W':
            longitude = -longitude
        latitude = gps_info[2]
        latitude = float(latitude[0][0]) / float(latitude[0][1]) + \
                   (float(latitude[1][0]) / float(latitude[1][1])) / 60.0
        if gps_info[1] == 'S':
            latitude = - latitude

        # Camera and lens
        camera = exif_info[272]
        if 42036 in exif_info:
            lens = exif_info[42036]
        else:
            lens = 'unknown'
        focal_length = 'ƒ/%f' % (float(exif_info[37386][0]) / float(exif_info[37386][1]))
        focal_length = focal_length.rstrip('0')
        f_number = '%.1fmm' % (float(exif_info[33437][0]) / float(exif_info[33437][1]))
        exposure_time = '%d/%ds' % (exif_info[33434][0], exif_info[33434][1])
        iso = 'ISO %d' % exif_info[34855]

        # Time
        taken_time = exif_info[36867]
        taken_time = taken_time.replace(':', '-', 2)

        camera_info_str = '%s\t%s\t%s\t%s\t%s\t%s' % (camera, lens, focal_length, f_number, exposure_time, iso)
        img_info_str = '%.4f\t%.4f\t%s' % (longitude, latitude, taken_time)
        return camera_info_str, img_info_str
