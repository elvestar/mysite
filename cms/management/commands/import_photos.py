# -*- coding: utf-8 -*-

import logging
import json
import re
from datetime import datetime, timedelta
import time
import json
import requests

from django.core.management.base import BaseCommand
from PIL import Image
from PIL.ExifTags import TAGS

from myssg.settings import Settings
from myssg.readers import Reader
from myssg.utils import Utils
from myssg.utils import ItemUtils
from cms.models import Photo


class Command(BaseCommand):
    help = 'Import photos to cms, correct gps coordinates, get locations in Chinese by using baidu api'

    def handle(self, *args, **options):
        logging.error('Begin to import photos to cms')
        settings = Settings()
        settings.CONTENT_DIR = '/Users/elvestar/github/elvestar/elvestar.github.io/'
        settings.IGNORE_DIRS.append('static')
        reader = Reader(settings)
        photo_items = list()
        for item in reader.read(force_all=True):
            if item.extension.lower() in ['jpg', 'png', 'gif'] and ItemUtils.is_life_item(item):
                if '1609-team-building' in item.uri:
                    photo_items.append(item)

        for item in photo_items:
            import_photo_item(item, force_update=False)


def import_photo_item(photo_item, force_update=False):
    photos = Photo.objects.filter(uri=photo_item.uri)
    if len(photos) > 0 and not force_update:
        return

    if len(photos) > 0:
        photo = photos[0]
    else:
        photo = Photo(uri=photo_item.uri)

    ak = 'CAc10b3a8d557c49bc2ffd46a7f2805a'
    im = Image.open(photo_item.path)
    exif_info = im._getexif()

    photo.width, photo.height = im.size

    # GPS info
    if 34853 not in exif_info:
        photo.has_gps_info = False
    else:
        photo.has_gps_info = True
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
        photo.longitude = longitude
        photo.latitude = latitude

        # Baidu coordinates correction
        photo.longitude_bd09 = longitude
        photo.latitude_bd09 = latitude
        geo_conv_url = 'http://api.map.baidu.com/geoconv/v1/?ak=%s&coords=%f,%f&from=1&to=5' % \
                       (ak, photo.longitude, photo.latitude)
        r = requests.get(geo_conv_url)
        if r.status_code == requests.codes.ok:
            ret = json.loads(r.text)
            if ret['status'] == 0:
                photo.longitude_bd09 = ret['result'][0]['x']
                photo.latitude_bd09 = ret['result'][0]['y']

        # Get address in chinese
        photo.address = 'unknown'
        reverse_geocode_url = 'http://api.map.baidu.com/geocoder/v2/?ak=%s&callback=renderReverse&location=%f,%f&output=json' % \
                              (ak, photo.latitude_bd09, photo.longitude_bd09)
        r = requests.get(reverse_geocode_url)
        if r.status_code == requests.codes.ok:
            ret = r.text.lstrip('renderReverse&&renderReverse(').rstrip(')')
            ret = json.loads(ret)
            if ret['status'] == 0:
                result = ret['result']
                address_component = result['addressComponent']
                photo.country_code = address_component['country_code']
                photo.city = address_component['city']
                if len(photo.city) == 0:
                    photo.city = address_component['province']
                if 'formatted_address' in result and len(result['formatted_address']) > 0:
                    photo.address = result['formatted_address']
                else:
                    address = address_component['country']
                    for k in ['province', 'city', 'district', 'street']:
                        if len(address_component[k]) > 0:
                            address += ', ' + address_component[k]
                    if address != '':
                        photo.address = address

        # Camera and lens
        if 272 in exif_info:
            photo.camera = exif_info[272]
        else:
            photo.camera = 'unknown'
        if 42036 in exif_info:
            photo.lens = exif_info[42036]
        else:
            photo.lens = 'unknown'
        photo.focal_length = float(exif_info[37386][0]) / float(exif_info[37386][1])
        photo.f_number = float(exif_info[33437][0]) / float(exif_info[33437][1])
        photo.exposure_time = float(exif_info[33434][0]) / float(exif_info[33434][1])
        photo.exposure_time_str = '%d/%ds' % (exif_info[33434][0], exif_info[33434][1])
        photo.iso = exif_info[34855]

        # Time
        taken_time = exif_info[36867]
        photo.taken_time = taken_time.replace(':', '-', 2)

        photo.save()
        logging.error('Success to import photo: %s' % photo.uri)
