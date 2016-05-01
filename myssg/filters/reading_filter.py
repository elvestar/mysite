# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from datetime import datetime

from bs4 import BeautifulSoup


def reading_note_filter(item):
    html_root = item.html_root
    h2 = html_root.find('h2')
    item.title = h2.string
    h2.parent['style'] = 'margin:0px auto; padding:5px; font-size:12pt; font-family:Times'
    # last_note = html_root.find('div', string=re.compile(r'\w*\d{4}-\d{2}-\d{2}\w*'))
    note_time_tags = html_root.find_all(['div', 'span'], text=re.compile(r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?'))
    if note_time_tags is not None:
        newest_note_time = datetime.fromtimestamp(0)
        newest_note_time_tag = None
        for time_tag in note_time_tags:
            time_str = time_tag.string
            if len(time_str) == 10:
                note_time = datetime.strptime(time_tag.string, '%Y-%m-%d')
            else:
                note_time = datetime.strptime(time_tag.string, '%Y-%m-%d %H:%M:%S')
            if note_time > newest_note_time:
                newest_note_time = note_time
                newest_note_time_tag = time_tag

        if newest_note_time_tag.name == 'div':
            newest_note_tag = newest_note_time_tag.next_sibling
        else:
            # There a empty tag
            print(item.uri)
            for child in reversed(list(newest_note_time_tag.parent.parent)):
                if child.name is None:
                    continue
                else:
                    newest_note_tag = child
                    # print(newest_note_tag)
                    break

            print(newest_note_tag.text)
        item.last_update = newest_note_tag.text
        item.last_update_time = newest_note_time

    item.html_root = html_root
