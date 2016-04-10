# -*- coding: utf-8 -*-

import os


class Writer(object):
    def __init__(self, settings):
        self.settings = settings
        self.output_dir = settings.OUTPUT_DIR
        pass

    def write(self, item, output):
        output_filepath = os.path.join(self.output_dir, item.uri + '.html')
        f = file(output_filepath, 'w')
        f.write(output)
        f.close()
