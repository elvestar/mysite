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

    def read(self):
        items = list()
        for file_item in self.get_file_items():
            content = file(file_item['path']).read()
            item = Item(uri=file_item['uri'],
                        extension=file_item['extension'],
                        content=content,
                        path=file_item['path'])
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
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            if len(files) > 20:
                files = files[0:20]
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

