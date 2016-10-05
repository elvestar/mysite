# -*- coding: utf-8 -*-
from __future__ import print_function

import copy
import re
from datetime import datetime
import os

from bs4 import BeautifulSoup

from myssg.items import Item
from myssg.utils import Utils
from myssg.settings import Settings
from cms.models import Photo


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
            img['src'] = '/' + item.uri.split('/')[0] + img['src'].lstrip('.')

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
    images['id'] = 'grid'
    for img in html_root.find_all('img'):
        new_img = soup.new_tag('img')
        new_img['data-action'] = 'zoom'
        new_img['src'] = img['src']
        new_img['alt'] = img['alt']
        if 'title' in img:
            new_img['title'] = img['title']

        image_uri, extension = os.path.splitext(new_img['src'].lstrip('/'))
        photo = Photo.objects.get(uri=image_uri)

        # focal_length = 'ƒ/%f' % (float(exif_info[37386][0]) / float(exif_info[37386][1]))
        # photo.focal_length = focal_length.rstrip('0')
        # photo.f_number = '%.1fmm' % (float(exif_info[33437][0]) / float(exif_info[33437][1]))
        # photo.exposure_time = '%d/%ds' % (exif_info[33434][0], exif_info[33434][1])
        # iso = 'ISO %d' % exif_info[34855]
        # # return camera_info_str, img_info_str
        # camera_info_str, img_info_str = Utils.parse_exif_info(exif_info)

        camera_info_str = '%s\t%s\t%fmm\tƒ/%f\t%s\tISO %d' % (photo.camera, photo.lens,
                                                          photo.focal_length, photo.f_number,
                                                          photo.exposure_time_str, photo.iso)
        image_info_str = '%.4f\t%.4f\t%s\t%s\t%s' % (photo.longitude_bd09, photo.latitude_bd09,
                                                     photo.taken_time.strftime('%Y-%m-%d %H:%M:%S'),
                                                     photo.address, photo.city)
        new_img['camera-info'] = camera_info_str
        new_img['image-info'] = image_info_str
        new_img['data-width'] = photo.width
        new_img['data-height'] = photo.height
        image = soup.new_tag('div')
        image.append(new_img)
        images.append(image)
    images_container = soup.new_tag('div')
    images_container['class'] = 'grid-wrapper container'
    images_container.append(images)
    gallery_tab = soup.new_tag('div')
    gallery_tab['class'] = 'tab-pane'
    gallery_tab['id'] = 'gallery'
    gallery_tab['role'] = 'tabpanel'
    gallery_tab.append(images_container)

    html_root['class'] = 'inner-container'
    article_tab = soup.new_tag('div')
    article_tab['class'] = 'tab-pane active'
    article_tab['id'] = 'article'
    article_tab['role'] = 'tabpanel'
    article_tab.append(html_root)

    map_tab = soup.new_tag('div', id='map')
    map_tab['class'] = 'tab-pane row'
    map_tab['role'] = 'tabpanel'
    map_body_tab = soup.new_tag('div', id='mapBody')
    # map_body_tab['id'] = 'map'
    map_body_tab['class'] = 'col-md-9'
    checkpoint_tab = soup.new_tag('div')
    checkpoint_tab['class'] = 'col-md-3'
    checkpoint_tab.append(soup.new_tag('div', id='checkpointList'))
    map_tab.append(map_body_tab)
    map_tab.append(checkpoint_tab)

    new_html_root = soup.new_tag('div')
    new_html_root['class'] = 'tab-content'
    new_html_root.append(article_tab)
    new_html_root.append(gallery_tab)
    new_html_root.append(map_tab)
    item.html_root = new_html_root


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


