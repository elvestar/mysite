# -*- coding: utf-8 -*-

from datetime import datetime

class Item(object):
    def __init__(self, uri, extension, content=None, path=None, mtime=None, html_root=None):
        self.uri = uri
        self.extension = extension
        self.content = content
        self.path = path
        self.mtime = mtime
        self.html_root = html_root

        self.description = 'No description'
        self.date = datetime.fromtimestamp(0)

    def __str__(self):
        return '%s, %s, %s' % (self.__class__.__name__, self.uri, self.extension)
