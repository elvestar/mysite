# -*- coding: utf-8 -*-

import logging
import json
import requests
from datetime import datetime
import os

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Import duokan notes'

    def handle(self, *args, **options):
        with open('../msv4/content/reading/notes/index.json') as data_file:
           book_info = json.load(data_file)
        print(book_info)
        book_info_dict = dict()
        for book in book_info['books']:
            book_info_dict[book['duokanbookid']] = book

        print(book_info_dict)

        notes_dir = '../contents/reading/notes/'
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
                print(book_id_div.string, duokanbookid)

                # 逐个解析笔记
                notes_list = list()
                for single_note_div in content_div.find_all('div', recursive=False):
                    note_div_children = list(single_note_div.find_all('div', recursive=False))
                    single_note = dict()
                    if len(note_div_children) == 2:
                        note_time_div, note_content_div = note_div_children
                        single_note['time'] = note_time_div.string
                        single_note['content'] = note_content_div.string

                    elif len(note_div_children) == 3:
                        note_time_div, note_content_div, comment_div = note_div_children
                        single_note['time'] = note_time_div.string
                        single_note['content'] = note_content_div.string
                        single_note['comment'] = comment_div.string
                    else:
                        # 可能是遇到了章节名了
                        if len(list(single_note_div.find_all('span', recursive=False))) == 1:
                            single_note['chapter'] = single_note_div.span.string
                    print(single_note)
                    notes_list.append(single_note)
                data['notes'] = notes_list

                # 将读书笔记以JSON格式写入文件
                if duokanbookid in book_info_dict:
                    book_uri = book_info_dict[duokanbookid]['uri']
                    data['title'] = book_uri
                    f = open('../msv4/content/reading/notes/%s.json' % book_uri, 'w')
                    f.write(json.dumps(data))
                    f.close()
            else:
                print('Not have en-note')



