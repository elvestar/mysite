# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from datetime import datetime

from bs4 import BeautifulSoup


def reading_note_filter(item):
    html_root = item.html_root
    item.title = html_root.find('h2').string
