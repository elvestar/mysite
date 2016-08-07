# -*- coding: utf-8 -*-

from datetime import datetime


class Item(object):
    def __init__(self, uri, extension, content=None, path=None, mtime=None, html_root=None, title=None):
        self.uri = uri
        self.extension = extension
        self.content = content
        self.path = path
        self.mtime = mtime
        self.html_root = html_root
        self.output = None
        self.final_output = None
        self.output_path = None

        self.date = datetime.fromtimestamp(0)
        self.time = None
        self.year = self.date.year
        self.month = self.date.month
        self.title = title
        self.sub_title = None
        self.summary = None
        self.last_update = None
        self.last_update_time = None
        self.is_event = False
        self.events = list()  # Events belong to item

    def __str__(self):
        return '%s, %s, %s' % (self.__class__.__name__, self.uri, self.extension)

    def __getitem__(self, item):
        return getattr(self, item)

    def update(self):
        self.year = self.date.year
        self.month = self.date.month
        self.mohth_str = self

