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

    # Find newest update note
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

        newest_note_tag = None
        if newest_note_time_tag.name == 'div':
            newest_note_tag = newest_note_time_tag.next_sibling
        else:
            # There a empty tag
            for child in reversed(list(newest_note_time_tag.parent.parent)):
                if child.name is None:
                    continue
                else:
                    newest_note_tag = child
                    # print(newest_note_tag)
                    break
        newest_note_time_tag['id'] = 'last-update'
        item.last_update = newest_note_tag.text
        item.last_update_time = newest_note_time

    # Book cover
    if '8d32c187-a076-465f-8717-08992a87ef3c' in item.uri:
        item.cover_url = 'https://img1.doubanio.com/lpic/s26384457.jpg'
    elif 'fa64eed0-8075-4d90-a484-7894cb0af870' in item.uri:
        item.cover_url = 'https://img3.doubanio.com/lpic/s21942845.jpg'
    elif '3609c6c1-807c-4497-8be7-d93898c61fa5' in item.uri:
        item.cover_url = 'https://img3.doubanio.com/lpic/s23139051.jpg'
    elif 'a28bc3c3-d0df-475e-8557-03272a437814' in item.uri:
        item.cover_url = 'https://img1.doubanio.com/lpic/s1790028.jpg'
    elif '439f1ecb-9f56-409d-acf7-0b7097deed81' in item.uri:
        item.cover_url = 'https://img1.doubanio.com/lpic/s5743437.jpg'
    elif 'fa47681a-b4b3-47e2-a303-5d03246e4658' in item.uri:
        item.cover_url = 'https://img3.doubanio.com/lpic/s4610502.jpg'
    else:
        item.cover_url = '/avatar.png'

    item.html_root = html_root
