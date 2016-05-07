# -*- coding: utf-8 -*-
from __future__ import print_function

import re
import logging

from bs4 import BeautifulSoup


def add_toc(item):
    soup = BeautifulSoup()
    html_root = item.html_root
    headings = html_root.find_all(re.compile('^h[2-3]'))
    toc = soup.new_tag('div', id='toc')
    cur_node = toc

    # if item.uri == 'notes/chromium-base-library':
    #     for child in html_root.children:
    #         print(child)
    last_level = 0
    for i, heading in enumerate(headings):
        # if item.uri == 'notes/chromium-base-library':
        #     print(heading)
        level = int(heading.name[1:])
        logging.debug('item[%s], cur_level[%d], last_level[%d]'
                      % (item.uri, level, last_level))

        if level > last_level:
            ul = soup.new_tag('ul')
            if i == 0:
                ul['class'] = "nav nav-stacked fixed"
            else:
                ul['class'] = "nav nav-stacked"
            cur_node.append(ul)
            li = create_toc_node(soup, heading)
            ul.append(li)
            cur_node = li
        elif level == last_level:
            li = create_toc_node(soup, heading)
            cur_node.parent.append(li)
            cur_node = li
        else:
            li = create_toc_node(soup, heading)
            cur_node.parent.parent.append(li)
            cur_node = li

        last_level = level
    item.toc = toc.prettify()


def create_toc_node(parent, heading):
    a = parent.new_tag('a', href='#' + heading['id'])
    if heading.text is not None:
        a.string = heading.text
    else:
        a.string = str(heading)
    li = parent.new_tag('li')
    li.append(a)
    return li
