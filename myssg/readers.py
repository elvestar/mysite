# -*- coding: utf-8 -*-

import os
import sys

from myssg.items import Item


# TODO 中文处理
reload(sys)
sys.setdefaultencoding('utf-8')

class Reader(object):
    def __init__(self):
        pass

    def read(self):
        d = './content'
        items = list()
        for filename in os.listdir(d):
            filepath = os.path.join(d, filename)
            url, extension = os.path.splitext(filename)
            extension = extension.strip('.')
            f = file(filepath)
            item = Item(url=url, extension=extension, content=file(filepath).read())
            items.append(item)
        return items

