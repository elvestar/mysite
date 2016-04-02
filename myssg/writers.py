# -*- coding: utf-8 -*-

import os


class Writer(object):
    def __init__(self):
        pass

    def write(self, item, template):
        output_dir = './output'
        output_filepath = os.path.join(output_dir, item.uri + '.html')
        f = file(output_filepath, 'w')
        config = {
            'language': 'zh-ch',
            'title': 'book'
        }
        page = {
            'dir': './'
        }
        html = template.render(item=item,
                               config=config,
                               page=page
                                )
        f.write(html)
        f.close()
