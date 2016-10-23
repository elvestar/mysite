# -*- coding: utf-8 -*-

import os
import sys
import time
import fnmatch
from datetime import datetime
import logging

from myssg.items import Item


# TODO 中文处理
reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)


class Reader(object):
    def __init__(self, settings):
        self.dir = settings.CONTENT_DIR
        self.settings = settings
        self.ignore_dirs = settings.IGNORE_DIRS
        self.ignore_files = settings.IGNORE_FILES

    def read(self, force_all=False):
        items = list()
        for file_item in self.get_file_items():
            # if 'org-mode' not in file_item['uri']:
            #     continue
            if not force_all:
                if file_item['uri'] not in [
                    'blog/learn-to-play-guitar',
                    # 'life/16Q1',
                    # 'life/16Q2',
                    # 'life/16Q3',
                    # 'life/1601-yuan-dan',
                    # 'life/1603-ba-ya',
                    # 'life/1603-hong-mi-3',
                    # 'life/1605-pa-huang-shan',
                    # 'life/16Q4',

                    # 'life/1504-team-building',
                    # 'life/1503-ikea',
                    # 'life/1503-feng-huang-ling',
                    # 'life/1504-qing-ming',
                    # 'life/1502-sony-e35',
                    # 'life/15Q1',
                    # 'life/15Q2',
                    # 'life/15Q3',
                    # 'life/15Q4',
                    # 'life/1502-the-last-day',
                    # 'notes/python-libs',

                    # 'notes/my-site-v2',
                    # 'life/1609-team-building',
                    # 'life/1511-learn-driving',

                    #  'life/1610',
                    # 'life/1610-guo-qing', 'life/1410-guo-qing',
                    # 'life/1510-guo-qing'
                ]:
                    continue
            # if not force_all:
            #     if file_item['uri'] not in ['life/1609-team-building', 'life/1610',
            #                                 'life/1610-guo-qing', 'life/1410-guo-qing', 'life/1510-guo-qing']:
            #         continue
            # if 'my-site-v' not in file_item['uri']:
            #     continue
            content = file(file_item['path']).read()
            item = Item(uri=file_item['uri'],
                        extension=file_item['extension'],
                        content=content,
                        path=file_item['path'])
            if item.uri.startswith(('notes/', 'life/', 'blog/')) and item.extension == 'html':
                logging.debug('Skip item:%s' % str(item))
                continue
            item.mtime = self.get_modify_datetime(item)
            items.append(item)
        return items

    def get_modify_datetime(self, item):
        try:
            ts = os.path.getmtime(item.path)
            return datetime.fromtimestamp(ts)
        except OSError as e:
            logging.warning('Caught Exception: %s', e)
            return None

    def get_file_items(self):
        for root, dirs, files in os.walk(self.dir, followlinks=True):
            upper_dir = root.replace(self.settings.CONTENT_DIR, '')
            if upper_dir != '':
                upper_dir += '/'
            dirs[:] = [d for d in dirs if '%s%s' % ((upper_dir, d)) not in self.ignore_dirs]
            # limit = 12
            # if len(files) > limit:
            #     files = files[0:limit]
            for f in files:
                if not any(fnmatch.fnmatch(f, ignore) for ignore in self.ignore_files):
                    try:
                        path = os.path.join(root, f)
                        uri, extension = os.path.splitext(path)
                        uri = uri.replace(self.dir, '')
                        extension = extension.strip('.')
                        file_item = {
                            'uri': uri,
                            'extension': extension,
                            'path': path
                        }
                        # time.sleep(1)
                        # print('New item: ', file_item)
                        yield file_item
                    except OSError as e:
                        logger.warning('Caught Exception: %s', e)

    def get_uri_set(self):
        uri_set = set()
        for file_item in self.get_file_items():
            uri_set.add(file_item['uri'])
        return uri_set

