# -*- coding: utf-8 -*-

import os


class Writer(object):
    def __init__(self):
        pass

    def write(self, item, template):
        output_dir = './output'
        output_filepath = os.path.join(output_dir, item.url + '.html')
        f = file(output_filepath, 'w')
        f.write(template.render(item=item))
        f.close()
