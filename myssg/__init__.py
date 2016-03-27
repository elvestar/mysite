# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import time
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader
import mistune

# TODO 不知道如何将当前目录加入PYTHONPATH
import sys
sys.path.append('./')

from myssg.readers import Reader, get_modify_datetime
from myssg.writers import Writer
from myssg.items import Item
from myssg.filters.add_toc import add_toc
from myssg.pyorg.pyorg import PyOrg


class MySSG(object):
    def __init__(self, settings=None):
        self.settiongs = settings
        self.all_items = None

    def run(self):
        start_time = time.time()
        reader = Reader()
        writer = Writer()
        env = Environment(loader=FileSystemLoader('./templates', ))
        template = env.get_template('blog.html')

        # Init filters
        markdown = mistune.Markdown()
        py_org = PyOrg()

        # Handle items using filters
        self.all_items = reader.read()
        for item in self.all_items:
            if item.extension == 'md':
                item.content = markdown(item.content)
            elif item.extension == 'org':
            # elif item.extension == 'org' and item.uri == 'test':
                item.content = py_org(item.content)
                add_toc(item)
            else:
                pass
            # if True:
            #     add_toc(item)
            writer.write(item, template)

        end_time = time.time()
        print('Done: use time {:.2f}'.format(end_time - start_time))

    def watch_items(self):
        while True:
            for item in self.all_items:
                new_mtime = get_modify_datetime(item.path)
                if new_mtime != item.mtime:
                    logging.warning(' * Detected change in %r, reloading' % item.path)
                    return
            time.sleep(1)


if __name__ == '__main__':
    while True:
        my_ssg = MySSG()
        my_ssg.run()
        # http_server = HTTPServer(('', 8000), BaseHTTPRequestHandler)
        # http_server.serve_forever()

        my_ssg.watch_items()


