# -*- coding: utf-8 -*-

import logging
import json
import requests
import re
import os
from os.path import isfile, join

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Modify uri for org file. Usage: python manage.py path old_uri new_uri'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('old_uri', type=str)
        parser.add_argument('new_uri', type=str)

    def handle(self, *args, **options):
        path = options['path']
        old_uri = options['old_uri']
        new_uri = options['new_uri']
        self.modify_uri(path, old_uri, new_uri)

    def modify_uri(self, path, old_uri, new_uri):
        old_fp = os.path.join(path, old_uri + '.org')
        new_fp = os.path.join(path, new_uri + '.org')
        old_img_path = os.path.join(path, '../static/imgs', old_uri)
        new_img_path = os.path.join(path, '../static/imgs', new_uri)
        if not os.path.exists(old_fp):
            logging.error('Modify failed! Old file path not exist: %s' % old_fp)
            return
        if os.path.exists(new_fp):
            logging.error('Modify failed! New file path exist: %s' % new_fp)
            return
        if os.path.exists(new_img_path):
            logging.error('Modify failed! New imgs path exist: %s' % new_img_path)
            return
        logging.error('Begin to modify uri, from %s to %s' % (old_uri, new_uri))

        # Modify org file content
        old_img_str = 'static/imgs/%s/' % old_uri
        new_img_str = 'static/imgs/%s/' % new_uri
        text = file(old_fp).read()
        text = text.replace(old_img_str, new_img_str)
        # print(text)
        open(old_fp, 'w').write(text)

        # Rename imgs path
        if os.path.exists(old_img_path):
            os.rename(old_img_path, new_img_path)

        # Rename org file path
        os.rename(old_fp, new_fp)
        logging.error('Success to modify uri, from %s to %s' % (old_uri, new_uri))




"""
# rename image
        path = '/Users/elvestar/github/elvestar/contents/notes/'
        for fn in os.listdir(path):
            fp = join(path, fn)
            if not isfile(join(fp)):
                logging.warning('Not file: %s' % fn)
                continue
            m = re.match(r'(.+).org$', fn)
            if m is not None:
                print(m.group(1))
                text = file(fp).read()

                re_1 = re.compile(r'(\[\[[^_]+)_(\d{1,14}\.(png|gif|jpg)\]\])')
                re_2 = re.compile(r'(#\+CAPTION: [^_]+)_(\d{1,14}\.(png|gif|jpg))')
                found = False
                for line in re_2.findall(text):
                    if not found:
                        found = True
                    print(line)
                if found:
                    print('Begin to re.sub', fp)
                    new_text = re_2.sub(r'\1/\2', text)
                    open(fp, 'w').write(new_text)
"""
