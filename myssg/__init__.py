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
from myssg.utils import Utils
from myssg.watcher import file_watcher, folder_watcher
from myssg.search import Searcher

import signal

g_stop = False


def signal_handler(signal, frame):
    os._exit(0)


class MySSG(object):
    def __init__(self, settings):
        self.settings = settings
        self.items = None
        self.templates = dict()
        self.reader = Reader(settings)
        self.writer = Writer(settings)
        self.searcher = Searcher()

        self.time_items = list()
        self.blog_items = list()
        self.reading_items = list()
        self.life_items = list()
        self.photos_items = list()
        self.items_group_by_year = list()
        self.events = list()
        self.events_group_by_year = list()
        self.env = None

    def run(self):
        start_time = time.time()
        self.env = Environment(loader=FileSystemLoader('./templates', ))
        template_names = ['note', 'blog', 'life',
                          'index', 'archives', 'timeline',
                          'time', 'time_analyzer',
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
                item.output = markdown(item.content)
            elif item.extension == 'org':
                py_org(item)
                org_filter(item)
                if item.uri.startswith(('notes/', 'blog/', 'life/')):
                    add_toc(item)
                    if item.uri.startswith('life/'):
                        photos_filter(item)
                elif item.uri == 'gallery':
                    gallery_filter(item)
                elif item.uri.startswith('photos/'):
                    photos_filter(item)
                item.output = item.html_root.prettify()
                # Search indexing
                self.searcher.add_document(item)
            elif item.extension == 'html':
                item.html_root = BeautifulSoup(item.content)
                if item.uri.startswith(('reading/notes/')):
                    reading_note_filter(item)
                item.output = item.html_root.prettify()
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

        self.searcher.commit()
        compile_end_time = time.time()

        # Set some global template variables
        self.set_template_context()

        for item in self.items:
            # Layout
            if item.extension in ['css', 'js', 'json', 'jpg', 'png', 'gif']:
                item.final_output = item.content
            elif item.uri in ['index', 'timeline', 'gallery', 'reading', 'archives',
                              'photos']:
                self.render_item_by_template(item, item.uri.replace('/', '_'))
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
                item.final_output = item.output

            # Router
            if item.extension in ['css', 'js', 'map']:
                item.output_path = item.uri + '.' + item.extension
            elif item.extension in ['png', 'jpg', 'gif']:
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

        # Events
        for item in self.items:
            if item.extension not in ['org', 'md']:
                continue
            self.events.append(item)
            if item.events is not None:
                self.events.extend(item.events)
        map(lambda it: it.update(), self.events)
        self.events.sort(key=itemgetter('date'), reverse=True)
        for year, events_of_year in groupby(self.events, itemgetter('year')):
            events_group_by_month = list()
            for month, events_of_month in groupby(events_of_year, itemgetter('month')):
                events_group_by_month.append((month, list(events_of_month)))
            self.events_group_by_year.append((year, events_group_by_month))

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

            events=self.events,
            events_group_by_year=self.events_group_by_year,

            item_url=Utils.item_url,
            item_date=Utils.item_date,
            item_date_slash=Utils.item_date_slash,
            item_date_short=Utils.item_date_short,
            item_datetime=Utils.item_datetime,
            to_date=Utils.to_date,
            to_date_slash=Utils.to_date_slash,
            to_date_short=Utils.to_date_short,
            to_datetime=Utils.to_datetime,
        )
        # self.env.filters['item_date'] = U

    def render_item_by_template(self, item, template_name):
        template = self.templates[template_name]
        item.final_output = template.render(item=item)
        return

    def generate_archives(self):
        pass
        # self.generate_reading_archives()
        # self.generate_time_stats()

    def generate_reading_archives(self):
        reading_archives_item = Item('reading_archives', 'json')
        reading_archives_item.output_path = 'reading/archives/index.html'
        template = self.templates['evernote']
        reading_archives_item.output = \
            template.render(item=reading_archives_item)
        self.writer.write(reading_archives_item)

    def generate_time_stats(self):
        start_time = time.time()
        ta = TimeAnalyzer(self.settings)
        html_roots = [item.html_root for item in self.time_items]
        ta.batch_analyze(html_roots)
        etl_end_time = time.time()
        ta.dump_all()
        dump_end_time = time.time()
        # clock_items = ta.query_clock_items_by_date(date='2016-04-16')
        end_time = time.time()
        print('Done[{:d} time items]: use time {:.2f}, etl time {:.2f}, dump time {:.2f}'
              .format(len(self.time_items), end_time - start_time, etl_end_time - start_time, dump_end_time - etl_end_time))

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
    signal.signal(signal.SIGINT, signal_handler)

    settings = Settings()
    watchers = {
        'content': folder_watcher(settings.CONTENT_DIR, [''], ['.#*']),
        'templates': folder_watcher(settings.TEMPLATES_DIR, [''], ['.#*'])
        }
    # 'mysite': folder_watcher(settings.SSG_DIR, [''], ['.#*'])
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


