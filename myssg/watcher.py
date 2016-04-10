# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import fnmatch
import logging


logger = logging.getLogger(__name__)


# Copy from pelican.utils
def folder_watcher(path, extensions, ignores=[]):
    '''Generator for monitoring a folder for modifications.

    Returns a boolean indicating if files are changed since last check.
    Returns None if there are no matching files in the folder'''

    def file_times(path):
        '''Return `mtime` for each file in path'''

        for root, dirs, files in os.walk(path, followlinks=True):
            dirs[:] = [x for x in dirs if not x.startswith(os.curdir)]

            for f in files:
                if f.endswith(tuple(extensions)) and \
                        not any(fnmatch.fnmatch(f, ignore) for ignore in ignores):
                    try:
                        yield os.stat(os.path.join(root, f)).st_mtime
                    except OSError as e:
                        logger.warning('Caught Exception: %s', e)

    last_mtime = 0
    while True:
        try:
            mtime = max(file_times(path))
            if mtime > last_mtime:
                last_mtime = mtime
                yield True
        except ValueError:
            yield None
        else:
            yield False


def file_watcher(path):
    '''Generator for monitoring a file for modifications'''
    LAST_MTIME = 0
    while True:
        if path:
            try:
                mtime = os.stat(path).st_mtime
            except OSError as e:
                logger.warning('Caught Exception: %s', e)
                continue

            if mtime > LAST_MTIME:
                LAST_MTIME = mtime
                yield True
            else:
                yield False
        else:
            yield None
