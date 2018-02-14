# -*- coding: utf-8 -*-

import logging
import json
import requests
import os
from os import listdir
from os.path import isfile, join

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '清理重复的raw照片'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        d = options['path']
        jpg_uri_list = list()
        for f in os.listdir(d):
            if f.startswith('._'):
                continue
            uri, ext = os.path.splitext(f)
            if ext in ['.jpg', '.JPG']:
                jpg_uri_list.append(uri)

        for f in os.listdir(d):
            if f.startswith('._'):
                continue
            uri, ext = os.path.splitext(f)
            if ext in ['.ARW', '.arw']:
                if uri not in jpg_uri_list:
                    file_path = os.path.join(d, f)
                    print('Delete file', file_path)
                    os.remove(file_path)
