# -*- coding: utf-8 -*-


class Item(object):
    def __init__(self, url, extension, content=None):
        self.url = url
        self.extension = extension
        self.content = content

    def __str__(self):
        return '%s, %s, %s' % (self.__class__.__name__, self.url, self.extension)
