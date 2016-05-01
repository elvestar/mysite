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
    item.last_note = 'hehehe'
    item.html_root = html_root
