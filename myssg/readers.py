# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
import logging

from myssg.items import Item


# TODO 中文处理
reload(sys)
sys.setdefaultencoding('utf-8')


class Reader(object):
    def __init__(self):
        self.dir = './content'
        pass

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
        file_items = list()
        for filename in os.listdir(self.dir):
            if filename.startswith('.#'):
                continue
            path = os.path.join(self.dir, filename)
            uri, extension = os.path.splitext(filename)
            extension = extension.strip('.')
            file_item = {
                'uri': uri,
                'extension': extension,
                'path': path
            }
            file_items.append(file_item)
        return file_items

    def get_uri_set(self):
        uri_set = set()
        for file_item in self.get_file_items():
            uri_set.add(file_item['uri'])
        return uri_set

