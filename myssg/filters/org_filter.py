# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from datetime import datetime

from bs4 import BeautifulSoup
from PIL import Image


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


def gallery_filter(item):
    soup = BeautifulSoup()
    html_root = item.html_root
    # print(html_root)
    pass


def gallery_album_filter(item):
    soup = BeautifulSoup()
    html_root = item.html_root
    images = soup.new_tag('div')
    images['class'] = 'Images grid'
    for img in html_root.find_all('img'):
        image = soup.new_tag('div')
        image['class'] = 'Image'
        image_overlay = soup.new_tag('div')
        image_overlay['class'] = 'Image-overlay'
        image.append(image_overlay)
        img['data-action'] = 'zoom'
        # set image size
        img_path = '/Users/elvestar/github/elvestar/contents/gallery/' + img['src']
        im = Image.open(img_path)
        h = 290
        width, height = im.size
        width = int(h * (float(width) / float(height)))
        height = h
        # print('Resize ', img_path, ' to ', width, 'x', height)
        # try:
        #     im = im.resize((width, height))
        #     im.save(img_path)
        # except Exception as e:
        #     pass
        img['data-width'] = width / 2
        img['data-height'] = height / 2
        image.append(img)
        images.append(image)
    container = soup.new_tag('div')
    container['class'] = 'Container'
    container.append(images)
    html_root.clear()
    html_root.append(container)
    # print(html_root)
    item.html_root = html_root


