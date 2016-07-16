# -*- coding: utf-8 -*-

import logging

from whoosh import index
from whoosh.fields import Schema, ID, TEXT
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser


class Searcher(object):
    schema = Schema(path=ID(stored=True, unique=True),
                    title=TEXT(field_boost=2.0, stored=True),
                    text=TEXT(analyzer=StemmingAnalyzer(), stored=True))

    def __init__(self):
        self.index_path = '.index'
        if index.exists_in(self.index_path):
            self.index = index.open_dir(self.index_path)
        else:
            self.index = index.create_in(self.index_path, schema=self.schema)
        self.qparser = QueryParser('text', self.schema)
        self.index_writer = self.index.writer()
        self.index_searcher = self.index.searcher()

    def add_document(self, item):
        self.index_writer.add_document(title=unicode(item.title), text=unicode(item.content), path=unicode(item.uri))
        logging.warning('%s is indexed' % (str(item)))

        # self.index_writer.add_document(title=u'ha ha', text=u'he he', path=u'/test')

    def commit(self):
        self.index_writer.commit()

    def search(self, q):
        results = self.index_searcher.search(self.qparser.parse(q))
        return results

if __name__ == '__main__':
    searcher = Searcher()
    q = 'UI Router'
    results = searcher.search(q)
    print(results)
    for result in results:
        print(result)
