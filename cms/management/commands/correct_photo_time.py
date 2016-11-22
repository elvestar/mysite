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
        photos_dir = '/Users/elvestar/Downloads/照片导出/WOW截图/'
        for f in listdir(photos_dir):
            if not f.endswith('.jpg'):
                continue
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





