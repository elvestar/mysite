# -*- coding: utf-8 -*-

import os


class Writer(object):
    def __init__(self, settings):
        self.settings = settings
        self.output_dir = settings.OUTPUT_DIR
        pass

    def write(self, item):
        path = os.path.join(self.output_dir, item.output_path)
        try:
            os.makedirs(os.path.dirname(path))
        except Exception:
            pass

        f = file(path, 'w')
        f.write(item.output)
        f.close()
