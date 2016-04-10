# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import logging
import threading
import time
from datetime import datetime, timedelta
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
from myssg.filters.org_filter import org_filter
from myssg.pyorg.time_analyzer import TimeAnalyzer
from myssg.pyorg.pyorg import PyOrg
from myssg.settings import Settings
from myssg.watcher import file_watcher, folder_watcher

import signal

g_stop = False


def signal_handler(signal, frame):
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)


class MySSG(object):
    def __init__(self, settings):
        self.settings = settings
        self.items = None
        self.templates = dict()
        self.reader = Reader(settings)
        self.writer = Writer(settings)
        self.time_items = list()

    def run(self):
        start_time = time.time()
        env = Environment(loader=FileSystemLoader('./templates', ))
        # env = Environment(loader=FileSystemLoader('./templates/gitbook', ))
        template_names = ['note', 'archives', 'tms']
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
                # continue
            elif item.extension == 'org':
            # elif item.extension == 'org' and item.uri in ['mysql', 'flask']:
            # elif item.extension == 'org' and item.uri in ['mysql', 'pyorg', 'time', '2015', '2016']:
                py_org(item)
                add_toc(item)
                org_filter(item)
                item.content = item.html_root.prettify()
            else:
                continue
            if item.uri in ['time', '2015', '2016']:
                self.time_items.append(item)
            output = template.render(item=item)
            self.writer.write(item, output)

        self.generate_archives()
        self.generate_time_stats()

        end_time = time.time()
        print('Done: use time {:.2f}'.format(end_time - start_time))

    def generate_archives(self):
        archives_item = Item('archives', 'json')
        template = self.templates['archives']
        output = template.render(items=self.items, item=archives_item)
        self.writer.write(archives_item, output)

    def generate_time_stats(self):
        tms_item = Item('tms', 'json')
        ta = TimeAnalyzer()
        html_roots = [item.html_root for item in self.time_items]
        ta.batch_analyze(html_roots)
        clock_items = ta.query_clock_items_by_date(date='2016-04-06')
        template = self.templates['tms']
        output = template.render(item=tms_item, clock_items=clock_items)
        self.writer.write(tms_item, output)

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
    settings = Settings()
    watchers = {'content': folder_watcher(settings.CONTENT_DIR,
                                          [''],
                                          ['.#*'])}
    while True:
        modified = {k: next(v) for k, v in watchers.items()}
        if any(modified.values()):
            logging.warning(' * Detected change, reloading')
            settings = Settings()
            my_ssg = MySSG(settings)
            my_ssg.run()

        time.sleep(0.5)

    # http_server = HTTPServer(('', 8000), MySSGRequestHandler)
    # logging.warning(' * Stop http server')
    # t = threading.Thread(target=http_server.serve_forever)
    # t.start()
    # logging.info(' * Start watching items')
    # my_ssg.watch_items()
    # http_server.shutdown()
    # logging.warning(' * Stop watching items')
    # t.join()


