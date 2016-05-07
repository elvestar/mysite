# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import logging
import time
import re
from datetime import datetime, timedelta
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler
from operator import itemgetter
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
import mistune
from bs4 import BeautifulSoup

# TODO 不知道如何将当前目录加入PYTHONPATH
import sys
sys.path.append('./')
# TODO 中文处理
reload(sys)
sys.setdefaultencoding('utf-8')

from myssg.readers import Reader
from myssg.writers import Writer
from myssg.items import Item
from myssg.filters.add_toc import add_toc
from myssg.filters.org_filter import org_filter, photos_filter, gallery_filter
from myssg.filters.reading_filter import reading_note_filter
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
        self.blog_items = list()
        self.reading_items = list()
        self.life_items = list()
        self.photos_items = list()
        self.items_group_by_year = list()
        self.env = None

    def run(self):
        start_time = time.time()
        self.env = Environment(loader=FileSystemLoader('./templates', ))
        template_names = ['note', 'blog', 'life',
                          'index', 'archives', 'timeline',
                          'time', 'tms', 'time_day', 'time_week',
                          'gallery', 'photos',
                          'reading', 'reading_note', 'reading_archives', 'evernote']
        for name in template_names:
            template = self.env.get_template('%s.html' % name)
            self.templates[name] = template

        # Init filters
        markdown = mistune.Markdown()
        py_org = PyOrg()

        self.items = self.reader.read()
        read_end_time = time.time()
        for item in self.items:
            # Filter
            if item.extension == 'html' and item.uri.startswith(('notes', 'blog', 'life', 'gallery')):
                continue

            # Compile
            if item.extension == 'md':
                item.content = markdown(item.content)
            elif item.extension == 'org':
                py_org(item)
                org_filter(item)
                if item.uri.startswith(('notes/', 'blog/', 'life/')):
                    add_toc(item)
                elif item.uri == 'gallery':
                    gallery_filter(item)
                elif item.uri.startswith('photos/'):
                    photos_filter(item)
                item.content = item.html_root.prettify()
            elif item.extension == 'html':
                item.html_root = BeautifulSoup(item.content)
                if item.uri.startswith(('reading/notes/')):
                    reading_note_filter(item)
                item.content = item.html_root.prettify()
            else:
                pass

            if item.extension in ['org', 'md', 'html']:
                if item.uri.startswith('blog/'):
                    self.blog_items.append(item)
                elif item.uri.startswith('reading/notes/'):
                    self.reading_items.append(item)
                elif item.uri.startswith('time/'):
                    self.time_items.append(item)
                elif item.uri.startswith('life/'):
                    self.life_items.append(item)
                elif item.uri.startswith('photos/'):
                    self.photos_items.append(item)

        compile_end_time = time.time()

        # 设置一些全局的模板变量
        self.set_template_context()

        for item in self.items:
            # Layout
            if item.extension in ['css', 'js', 'json', 'jpg', 'png']:
                item.output = item.content
            elif item.uri in ['index', 'timeline', 'gallery', 'reading', 'archives', 'photos']:
                self.render_item_by_template(item, item.uri)
            elif item.uri.startswith('notes'):
                self.render_item_by_template(item, 'note')
            elif item.uri.startswith('blog'):
                self.render_item_by_template(item, 'blog')
            elif item.uri.startswith('life'):
                self.render_item_by_template(item, 'life')
            elif item.uri.startswith('time'):
                self.render_item_by_template(item, 'time')
            elif item.uri.startswith('photos'):
                self.render_item_by_template(item, 'photos')
            elif item.uri.startswith('gallery/'):
                self.render_item_by_template(item, 'gallery_album')
            elif item.uri.startswith('reading/notes/'):
                self.render_item_by_template(item, 'evernote')
            else:
                item.output = item.content

            # Router
            if item.extension in ['css', 'js', 'map']:
                item.output_path = item.uri + '.' + item.extension
            elif item.extension in ['png', 'jpg']:
                m = re.match(r'(.+)/(imgs/(.+)_\d+)', item.uri)
                if m is None:
                    item.output_path = item.uri + '.' + item.extension
                else:
                    item.output_path = m.group(1) + '/' + m.group(3) + '/' + m.group(2) + '.' + item.extension
            elif item.uri == 'index':
                item.output_path = 'index.html'
            elif item.extension in ['org', 'md', 'html']:
                item.output_path = item.uri + '/index.html'
            elif item.extension is None:
                item.output_path = item.uri
            else:
                item.output_path = item.uri + '.' + item.extension

            # Output
            self.writer.write(item)

        layout_end_time = time.time()

        self.generate_archives()
        archive_end_time = time.time()

        end_time = time.time()
        print('Done[{:d} items]: use time {:.2f}, read time {:.2f}, complie time {:.2f}, layout time {:.2f}, archive time {:.2f}'
              .format(len(self.items), end_time - start_time, read_end_time - start_time, compile_end_time - read_end_time,
                      layout_end_time - compile_end_time, archive_end_time - layout_end_time))

    def set_template_context(self):
        map(lambda it: it.update(), self.items)
        self.items.sort(key=itemgetter('date'), reverse=True)
        for year, item_of_year in groupby(self.items, itemgetter('year')):
            self.items_group_by_year.append((year, list(item_of_year)))
        self.reading_items.sort(key=itemgetter('last_update_time'), reverse=True)
        self.blog_items.sort(key=itemgetter('date'), reverse=True)
        self.life_items.sort(key=itemgetter('date'), reverse=True)
        self.env.globals.update(
            items=self.items,
            items_group_by_year=self.items_group_by_year,
            time_items=self.time_items,
            reading_items=self.reading_items,
            blog_items=self.blog_items,
            life_items=self.life_items,
            photos_items=self.photos_items,
        )

    def render_item_by_template(self, item, template_name):
        template = self.templates[template_name]
        item.output = template.render(item=item)
        return

    def generate_archives(self):
        # archives_item = Item('archives', 'json')
        # archives_item.output_path = 'archives/index.html'
        # template = self.templates['archives']
        # archives_item.output = template.render(item=archives_item)
        # self.writer.write(archives_item)

        self.generate_reading_archives()
        # self.generate_time_stats()

    def generate_reading_archives(self):
        reading_archives_item = Item('reading_archives', 'json')
        reading_archives_item.output_path = 'reading/archives/index.html'
        template = self.templates['evernote']
        reading_archives_item.output = \
            template.render(item=reading_archives_item)
        self.writer.write(reading_archives_item)

    def generate_time_stats(self):
        tms_item = Item('time/tms', 'json')
        tms_item.title = '时间分析'
        tms_item.output_path = 'time/day/index.html'
        ta = TimeAnalyzer()
        html_roots = [item.html_root for item in self.time_items]
        # ta.batch_analyze(html_roots)
        # clock_items = ta.query_clock_items_by_date(date='2016-04-16')
        template = self.templates['time_day']
        tms_item.output = template.render(item=tms_item)
        self.writer.write(tms_item)

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
    watchers = {
        'content': folder_watcher(settings.CONTENT_DIR, [''], ['.#*']),
        'templates': folder_watcher(settings.TEMPLATES_DIR, [''], ['.#*'])
        }
    # 'myssg': folder_watcher(settings.SSG_DIR, [''], ['.#*'])
    while True:
        modified = {k: next(v) for k, v in watchers.items()}
        if any(modified.values()):
            logging.warning(' * Detected change, reloading')
            settings = Settings()
            my_ssg = MySSG(settings)
            my_ssg.run()

        time.sleep(1)

        # http_server = HTTPServer(('', 8000), MySSGRequestHandler)
        # logging.warning(' * Stop http server')
        # t = threading.Thread(target=http_server.serve_forever)
        # t.start()
        # logging.info(' * Start watching items')
        # my_ssg.watch_items()
        # http_server.shutdown()
        # logging.warning(' * Stop watching items')
        # t.join()


