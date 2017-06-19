# -*- coding: utf-8 -*-

import logging
import json
import requests
import os
from os import listdir
from os.path import isfile, join

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Remove unused images of org'

    def add_arguments(self, parser):
        parser.add_argument('uri', type=str)

    def handle(self, *args, **options):
        root_path = '/Users/elvestar/github/elvestar/msv4/content/'
        imgs_root_dir = '/Users/elvestar/github/elvestar/msv4/content/static/imgs/'
        uri = options['uri']
        imgs_dir = os.path.join(imgs_root_dir, uri.split('/')[-1])
        org_file_path = os.path.join(root_path, uri + '.org')
        print(imgs_dir, org_file_path)
        imgs_file_in_org_file = list()
        for line in file(org_file_path):
            if 'static/imgs/' in line:
                img_path_in_org_file = line.strip('\n').strip().split('/')[-1].rstrip(']')
                imgs_file_in_org_file.append(img_path_in_org_file)

        dest_dir = os.path.join(root_path, 'bak', uri.split('/')[-1])
        try:
            os.mkdir(dest_dir)
        except Exception as e:
            print('%s is existent' % dest_dir)

        for img_file in os.listdir(imgs_dir):
            if img_file not in imgs_file_in_org_file:
                print(img_file)
                img_path = os.path.join(imgs_dir, img_file)
                dest_path = os.path.join(dest_dir, img_file)

                os.rename(img_path, dest_path)
                

