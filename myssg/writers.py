# -*- coding: utf-8 -*-

import os
import datetime
import logging

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from cms.models import FileItem


class Writer(object):
    def __init__(self, settings):
        self.settings = settings
        self.output_dir = settings.OUTPUT_DIR
        pass

    def write(self, item):
        try:
            if item.extension in ['org']:
                file_item = FileItem.objects.filter(uri=item.uri)
                if file_item is not None:
                    file_item.delete()
                file_item = FileItem(uri=item.uri, mtime=item.mtime, date=item.date,
                                     content=item.content, output=item.output, file_size=len(item.content))
                if item.title is None:
                    file_item.title = item.uri
                else:
                    file_item.title = item.title
                file_item.save()

            path = os.path.join(self.output_dir, item.output_path)
            try:
                os.makedirs(os.path.dirname(path))
            except Exception:
                pass

            f = file(path, 'w')
            f.write(item.final_output)
            f.close()
        except Exception as e:
            logging.error('item:%s, expection:%s' % (item, str(e)))
