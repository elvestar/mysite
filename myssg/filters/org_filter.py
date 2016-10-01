# -*- coding: utf-8 -*-
from __future__ import print_function

import copy
import re
from datetime import datetime

from bs4 import BeautifulSoup
from PIL import Image

from myssg.items import Item


def org_filter(item):
    html_root = item.html_root

    h1 = html_root.body.h1
    if h1 is not None:
        h1.decompose()

    title = html_root.head.title
    if title is not None:
        item.title = title.string
    else:
        item.title = item.uri

    # Image zoom
    for img in html_root.find_all('img'):
        img['data-action'] = 'zoom'
        if img['src'].startswith('./imgs/'):
            img['src'] = '/' + item.uri + '/imgs/' + img['src'].split('/')[-1]

    # Set org item meta (such as date, tags)
    for meta in html_root.find_all('meta'):
        meta_name = meta['name']
        meta_content = meta['content']
        if meta_name == 'date':
            item.date = datetime.strptime(meta_content, '%Y-%m-%d')
        elif meta_name == 'filetags':
            item.tags = re.split(r' {2,}', meta_content)
        else:
            setattr(item, meta_name, meta_content)

    # Set org item summary
    first_p = html_root.body.find(['p', 'ul', 'table'])
    if first_p is None:
        item.summary = 'No summary'
    else:
        item.summary = first_p.text

    item.html_root = html_root.body
    item.html_root.name = 'article'
    extract_events(item)


def gallery_filter(item):
    soup = BeautifulSoup()
    html_root = item.html_root
    # print(html_root)
    pass


def photos_filter(item):
    soup = BeautifulSoup()
    html_root = item.html_root
    images = soup.new_tag('div')
    images['class'] = 'grid'
    for img in html_root.find_all('img'):
        new_img = soup.new_tag('img')
        new_img['data-action'] = 'zoom'
        new_img['src'] = img['src']
        new_img['alt'] = img['alt']
        # # set image size
        img_path = '/Users/elvestar/github/elvestar/elvestar.github.io/' + new_img['src']
        im = Image.open(img_path)
        width, height = im.size
        new_img['data-width'] = width
        new_img['data-height'] = height
        image = soup.new_tag('div')
        image.append(new_img)
        images.append(image)
    container = soup.new_tag('div')
    container['class'] = 'grid-wrapper'
    container.append(images)
    # html_root.clear()
    html_root.append(container)
    item.html_root = html_root


event_tag_names = ['h2', 'h2', 'h3', 'h4', 'h5', 'h6']


def extract_events(item):
    soup = BeautifulSoup()
    html_root = item.html_root
    event_tags = html_root.find_all(event_tag_names, text=re.compile(r'<\d{4}-\d{2}-\d{2}.*>'))
    for event_tag in event_tags:
        event_time = None
        m = re.match(r'(.*?)\s*<(\d{4}-\d{2}-\d{2}).*(\d{2}:\d{2})>', event_tag.string)
        if m is None:
            m = re.match(r'(.*?)\s*<(\d{4}-\d{2}-\d{2}).*>', event_tag.string)
            time_str = m.group(2)
            event_date = datetime.strptime(time_str, '%Y-%m-%d')
            event_anchor = event_date.strftime('%Y%m%d')
        else:
            time_str = m.group(2) + ' ' + m.group(3)
            event_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            event_date = event_time
            event_anchor = event_time.strftime('%Y%m%d-%H%M')
        event_tag['id'] = event_anchor

        event_title = m.group(1)
        event_html_root = soup.new_tag('article')
        next_sibling = event_tag.next_sibling
        while next_sibling is not None and next_sibling.name not in event_tag_names:
            copied_element = BeautifulSoup(str(next_sibling))
            event_html_root.append(copied_element)
            # event_html_root.append(copy.copy(next_sibling))
            next_sibling = next_sibling.next_sibling

        event = Item(uri=item.uri + '/#' + event_anchor,
                     extension='event',
                     content=event_html_root.prettify())
        event.date = event_date
        if event_time is not None:
            event.time = event_time
        event.title = event_title
        event.is_event = True
        first_p = event_tag.next_sibling
        if first_p is None:
            event.summary = 'No summary'
        else:
            event.summary = first_p.text
        item.events.append(event)


