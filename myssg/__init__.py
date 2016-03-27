# -*- coding: utf-8 -*-
from __future__ import print_function

import time

from jinja2 import (BaseLoader, ChoiceLoader, Environment, FileSystemLoader,
                    PrefixLoader, TemplateNotFound)
import mistune

# TODO 不知道如何将当前目录加入PYTHONPATH
import sys
sys.path.append('./')

from myssg.readers import Reader
from myssg.writers import Writer
from myssg.items import Item
from myssg.filters.add_toc import add_toc
from myssg.pyorg.pyorg import PyOrg


class MySSG(object):
    def __init__(self, settings=None):
        self.settiongs = settings

    def run(self):
        start_time = time.time()
        reader = Reader()
        writer = Writer()
        env = Environment(loader=FileSystemLoader('./templates', ))
        template = env.get_template('blog.html')

        # Init filters
        markdown = mistune.Markdown()
        py_org = PyOrg()

        # Handle items using filters
        all_items = reader.read()
        for item in all_items:
            if item.extension == 'md':
                item.content = markdown(item.content)
            elif item.extension == 'org':
            # elif item.extension == 'org' and item.uri == 'test':
                item.content = py_org(item.content)
                add_toc(item)
            else:
                pass
            # if True:
            #     add_toc(item)
            writer.write(item, template)

        end_time = time.time()
        print('Done: use time {:.2f}'.format(end_time - start_time))


if __name__ == '__main__':
    my_ssg = MySSG()
    my_ssg.run()


