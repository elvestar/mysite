# -*- coding: utf-8 -*-

import time

from jinja2 import (BaseLoader, ChoiceLoader, Environment, FileSystemLoader,
                    PrefixLoader, TemplateNotFound)

# TODO 不知道如何将当前目录加入PYTHONPATH
import sys
sys.path.append('./')

from myssg.readers import Reader
from myssg.writers import Writer
from myssg.items import Item


class MySSG(object):
    def __init__(self, settings):
        self.settiongs = settings

    def run(self):
        start_time = time.time()
        reader = Reader()
        writer = Writer()
        env = Environment(loader=FileSystemLoader('./templates', ))
        template = env.get_template('blog.html')

        all_items = reader.read()
        for item in all_items:
            writer.write(item, template)

if __name__ == '__main__':
    settings = dict()
    ssg = MySSG(settings)
    ssg.run()


