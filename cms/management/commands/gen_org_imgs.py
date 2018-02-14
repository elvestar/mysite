# -*- coding: utf-8 -*-

import logging
import json
import requests
import os
from os import listdir
from os.path import isfile, join

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate org image with caption'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('uri', type=str)

    def handle(self, *args, **options):
        path = options['path']
        uri = options['uri']
        # mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        # for f in list(sorted(listdir(path), key=mtime)):
        for f in list(sorted(listdir(path))):
            if not isfile(join(path, f)):
                logging.warning('Not file: %s' % f)
                continue
            image_path = '../static/imgs/%s/%s' % (uri, f)
            print('#+CAPTION: %s' % image_path)
            print('[[%s]]' % image_path)
