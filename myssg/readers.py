# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

from myssg.items import Item


# TODO 中文处理
reload(sys)
sys.setdefaultencoding('utf-8')


def get_modify_datetime(path):
    return datetime.fromtimestamp(os.path.getmtime(path))


class Reader(object):
    def __init__(self):
        pass

    def read(self):
        d = './content'
        items = list()
        for filename in os.listdir(d):
            path = os.path.join(d, filename)
            uri, extension = os.path.splitext(filename)
            extension = extension.strip('.')
            item = Item(uri=uri,
                        extension=extension,
                        content=file(path).read(),
                        path=path,
                        mtime=get_modify_datetime(path))
            items.append(item)
        return items

