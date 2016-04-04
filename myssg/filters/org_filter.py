# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from datetime import datetime

from bs4 import BeautifulSoup


def org_filter(item):
    html_root = item.html_root

    title = html_root.head.title
    if title is not None:
        item.title = title.string
    else:
        item.title = item.uri

    for meta in html_root.find_all('meta'):
        meta_name = meta['name']
        meta_content = meta['content']
        if meta_name == 'date':
            item.date = datetime.strptime(meta_content, '%Y-%m-%d')
        elif meta_name == 'filetags':
            item.tags = re.split(r' {2,}', meta_content)
        else:
            setattr(item, meta_name, meta_content)

    h1 = html_root.body.h1
    if h1 is not None:
        h1.decompose()

    item.html_root = html_root.body
