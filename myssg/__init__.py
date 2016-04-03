# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import logging
import threading
import time
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader
import mistune

# TODO 不知道如何将当前目录加入PYTHONPATH
import sys
sys.path.append('./')

from myssg.readers import Reader
from myssg.writers import Writer
from myssg.items import Item
from myssg.filters.add_toc import add_toc
from myssg.pyorg.pyorg import PyOrg

import signal

g_stop = False


def signal_handler(signal, frame):
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)


class MySSG(object):
    def __init__(self, settings=None):
        self.settings = settings
        self.items = None
        self.templates = dict()
        self.reader = Reader()
        self.writer = Writer()

    def run(self):
        start_time = time.time()
        env = Environment(loader=FileSystemLoader('./templates', ))
        # env = Environment(loader=FileSystemLoader('./templates/gitbook', ))
        template_names = ['note', 'archives']
        # template_names = ['website/page']
        for name in template_names:
            template = env.get_template('%s.html' % name)
            self.templates[name] = template

        # Init filters
        markdown = mistune.Markdown()
        py_org = PyOrg()

        # Handle items using filters
        self.items = self.reader.read()
        for item in self.items:
            template = self.templates['note']
            # template = self.templates['website/page']
            if item.extension == 'md':
                item.content = markdown(item.content)
            # elif item.extension == 'org':
            # elif item.extension == 'org' and item.uri in ['mysql', 'flask']:
            elif item.extension == 'org' and item.uri in ['mysql', 'pyorg', 'flask']:
                item.content = py_org(item.content)
                add_toc(item)
            else:
                pass
            output = template.render(item=item)
            self.writer.write(item, output)

        self.generate_archives()

        end_time = time.time()
        print('Done: use time {:.2f}'.format(end_time - start_time))

    def generate_archives(self):
        archives_item = Item('archives', 'json')
        template = self.templates['archives']
        output = template.render(items=self.items, item=archives_item)
        self.writer.write(archives_item, output)

    def watch_items(self):
        uri_set = set()
        for item in self.items:
            uri_set.add(item.uri)
        while True:
            for item in self.items:
                new_mtime = self.reader.get_modify_datetime(item)
                if new_mtime is None:
                    continue
                if new_mtime != item.mtime:
                    logging.warning(' * Detected update in %r, reloading' % item.path)
                    return

            new_uri_set = self.reader.get_uri_set()
            added_uri_set = new_uri_set.difference(uri_set)
            if len(added_uri_set) > 0:
                logging.warning(' * Detected add in %r, reloading' % added_uri_set)
                return
            deleted_uri_set = uri_set.difference(new_uri_set)
            if len(deleted_uri_set) > 0:
                logging.warning(' * Detected delete in %r, reloading' % deleted_uri_set)
                return

            time.sleep(1)


class MySSGRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # self.path = 'output/' + self.path
        SimpleHTTPRequestHandler.do_GET(self)


if __name__ == '__main__':
    http_server = HTTPServer(('', 8000), MySSGRequestHandler)
    while True:
        my_ssg = MySSG()
        my_ssg.run()
        t = threading.Thread(target=http_server.serve_forever)
        t.start()

        logging.info(' * Start watching items')
        my_ssg.watch_items()
        logging.warning(' * Stop watching items')
        http_server.shutdown()
        logging.warning(' * Stop http server')
        t.join()


