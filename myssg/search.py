# -*- coding: utf-8 -*-

import logging

from elasticsearch import Elasticsearch


class Searcher(object):

    def __init__(self):
        self.es = Elasticsearch()

    def add_document(self, item):
        doc = {
           'title': item.title,
           'summary': item.summary,
           'content': item.content,
        }
        res = self.es.index(index='pkm', doc_type='item', id=item.uri, body=doc)
        print(res)

    def commit(self):
        pass

    def search(self, q):
        pass

if __name__ == '__main__':
    searcher = Searcher()
    q = 'test'
    results = searcher.search(q)
    for result in results:
        print(result)
