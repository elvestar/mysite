# -*- coding: utf-8 -*-


class Item(object):
    def __init__(self, uri, extension, content=None):
        self.uri = uri
        self.extension = extension
        self.content = content

    def __str__(self):
        return '%s, %s, %s' % (self.__class__.__name__, self.uri, self.extension)
