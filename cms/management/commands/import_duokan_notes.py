# -*- coding: utf-8 -*-

import logging
import json
import requests
from datetime import datetime, timedelta
import os

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from PIL import Image


class Command(BaseCommand):
    help = 'Import duokan notes'

    def handle(self, *args, **options):
        with open('../msv4/content/reading/notes/index.json') as data_file:
           book_info = json.load(data_file)
        book_info_dict = dict()
        for book in book_info['books']:
            book_info_dict[book['duokanbookid']] = book


        notes_dir = '../contents/reading/notes/'
        # for note_fn in ['ce171565-77d5-447e-821b-85dcdcc28275.html']:
        for note_fn in os.listdir(notes_dir):
            note_path = notes_dir + '/' + note_fn
            print('note_path: ', note_path)
            file_size = os.path.getsize(note_path)
            file_content = file(note_path).read(file_size)
            soup = BeautifulSoup(file_content)
            en_note_tag = getattr(soup, 'en-note')
            data = dict()
            if en_note_tag is not None:
                content_div, book_id_div = list(en_note_tag.find_all('div', recursive=False))

                # 解析获取多看图书id
                duokanbookid = book_id_div.string.replace('duokanbookid:', '')
                data['duokanbookid'] = duokanbookid

                # 逐个解析笔记
                notes_list = list()
                for single_note_div in content_div.find_all('div', recursive=False):
                    note_div_children = list(single_note_div.find_all('div', recursive=False))
                    single_note = dict()
                    if len(note_div_children) == 2:
                        note_time_div, note_content_div = note_div_children
                        single_note['time'] = note_time_div.string
                        single_note['content'] = note_content_div.get_text('\n')

                        if len(single_note_div.find_all('table', recursive=False)) >= 1:
                            td_1, td_2 = single_note_div.table.find_all('td')
                            single_note['comment'] = td_2.string
                    else:
                        # 可能是遇到了章节名了
                        if len(list(single_note_div.find_all('span', recursive=False))) == 1:
                            chapter = single_note_div.span.string
                            if chapter.startswith('多看笔记 来自多看阅读'):
                                continue
                            single_note['chapter'] = chapter
                    notes_list.append(single_note)
                data['notes'] = notes_list

                # 将读书笔记以JSON格式写入文件
                if duokanbookid in book_info_dict:
                    book_uri = book_info_dict[duokanbookid]['uri']

                    # 遍历读书截图，并在笔记列表里找到对应的笔记
                    book_imgs_dir = '../msv4/content/reading/imgs/%s/' % book_uri
                    if os.path.exists(book_imgs_dir):
                        for book_img_fn in os.listdir(book_imgs_dir):
                            book_img_path = '%s/%s' % (book_imgs_dir, book_img_fn)
                            im = Image.open(book_img_path)
                            exif_info = im._getexif()
                            if exif_info is None:
                                logging.warning('%s has a None EXIF' % str(book_img_path))
                                continue
                            img_taken_time = datetime.strptime(exif_info[36867], '%Y:%m:%d %H:%M:%S')
                            print(book_img_path, img_taken_time)
                            min_time_diff = timedelta(days=366)
                            corresponding_note = None
                            for note in data['notes']:
                                if 'time' not in note:
                                    continue
                                note_time = datetime.strptime(note['time'], '%Y-%m-%d %H:%M:%S')
                                # 我总是先截图，然后记笔记
                                time_diff = note_time - img_taken_time
                                if note_time >= img_taken_time and time_diff < timedelta(seconds=300):
                                    if time_diff < min_time_diff:
                                        min_time_diff = time_diff
                                        corresponding_note = note
                            if corresponding_note is not None:
                                # 找到截图对应的笔记了！
                                print(corresponding_note)
                                corresponding_note['img_path'] = '/reading/imgs/%s/%s' % (book_uri, book_img_fn)
                                corresponding_note['img_taken_time'] = img_taken_time.strftime('%Y-%m-%d %H:%M:%S')

                    data['title'] = book_info_dict[duokanbookid]['title']
                    data['date'] = book_info_dict[duokanbookid]['date']
                    data['source'] = note_fn
                    f = open('../msv4/content/reading/notes/%s.json' % book_uri, 'w')
                    f.write(json.dumps(data))
                    f.close()
            else:
                print('Not have en-note')



