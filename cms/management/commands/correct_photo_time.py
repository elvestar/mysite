# -*- coding: utf-8 -*-

import logging
import json
import requests
from datetime import datetime, timedelta
import os
from os import listdir
from os.path import isfile, join

from django.core.management.base import BaseCommand

from PIL import Image
import pexif


class Command(BaseCommand):
    help = 'Collect taken time of photo exif'

    def handle(self, *args, **options):
        # photos_dir = '/Users/elvestar/Downloads/照片导出/WOW截图/'
        # photos_dir = '/Users/elvestar/Downloads/照片导出/FF10截图'
        # photos_dir = '/Users/elvestar/Downloads/照片导出/iqiyi_jietu'
        photos_dir = '/Users/elvestar/Pictures/华为导出'
        for f in listdir(photos_dir):
            self.correct_huawei_screenshot_time(photos_dir, f)

    def correct_huawei_screenshot_time(self, photos_dir, f):
        if not f.endswith('.jpg'):
            return
        photo_path = os.path.join(photos_dir, f)
        img = pexif.JpegFile.fromFile(photo_path)
        dt = datetime.strptime(f, "Screenshot_%Y%m%d-%H%M%S.jpg")
        img.exif.primary.Model = 'HUAWEI Mate 10'
        img.exif.primary.DateTime = dt.strftime('%Y:%m:%d %H:%M:%S')
        img.writeFile(photo_path)
        print(f, dt)

    def correct_iqiyi_screenshot_time(self, photos_dir, f):
        if not f.endswith('.jpg'):
            return
        photo_path = os.path.join(photos_dir, f)
        img = pexif.JpegFile.fromFile(photo_path)
        dt = datetime.strptime(f, "%Y-%m-%d %H'%M'%S.jpg")
        img.exif.primary.Model = 'DELL U2412M'
        img.exif.primary.DateTime = dt.strftime('%Y:%m:%d %H:%M:%S')
        img.writeFile(photo_path)
        print(f, dt)

    def correct_steam_screenshot_time(self, photos_dir, f):
        if not f.endswith('.jpg'):
            return
        photo_path = os.path.join(photos_dir, f)
        img = pexif.JpegFile.fromFile(photo_path)
        dt = datetime.strptime(f, '%Y%m%d%H%M%S_1.jpg')
        img.exif.primary.Model = 'DELL U2412M'
        img.exif.primary.DateTime = dt.strftime('%Y:%m:%d %H:%M:%S')
        img.writeFile(photo_path)
        print(f, dt)


    def correct_wow_and_m8_screenshot_time(self, photos_dir, f):
        if not f.endswith('.jpg'):
            return
        photo_path = os.path.join(photos_dir, f)
        img = pexif.JpegFile.fromFile(photo_path)

        if f.startswith('WoWScrnShot_'):
            dt = datetime.strptime(f, 'WoWScrnShot_%m%d%y_%H%M%S.jpg')
            print(f, dt)
            img.exif.primary.Model = 'DELL U2412M'
            img.exif.primary.DateTime = dt.strftime('%Y:%m:%d %H:%M:%S')
            img.writeFile(photo_path)
        elif len(f) == 14 and f[6] == 'A':
            # Like 100117A003.jpg
            dt_in_file = datetime.strptime(f[0:6], '%y%m%d')
            dt_in_exif = datetime.strptime(img.exif.primary.DateTime, '%Y:%m:%d %H:%M:%S')
            days_diff = (dt_in_file - dt_in_exif).days
            if abs(days_diff) >= 3:
                print(f, dt_in_file, dt_in_exif)
                # img.exif.primary.DateTime = dt_in_file.strftime('%Y:%m:%d %H:%M:%S')
                # img.writeFile(photo_path)
        elif f.startswith('PrtScn20'):
            dt = datetime.strptime(f, 'PrtScn%Y%m%d%H%M%S.jpg')
            print(f, dt)
            img.exif.primary.DateTime = dt.strftime('%Y:%m:%d %H:%M:%S')
            img.writeFile(photo_path)
