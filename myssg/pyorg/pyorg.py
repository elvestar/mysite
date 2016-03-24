# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import re

from bs4 import BeautifulSoup


def _gen_org_re_for_begin_end(key):
    return (r'^ *#\+(?:BEGIN_%s|begin_%s) *\n'
            r'([\s\S]+?)\s*'
            r' *#\+(?:END_%s|end_%s) *(?:\n+|$)'
            %
            (key.upper(), key, key.upper(), key))


def _pure_pattern(regex):
    pattern = regex.pattern
    if pattern.startswith('^'):
        pattern = pattern[1:]
    return pattern


class Rules(object):
    newline = re.compile(r'^\n+')
    heading = re.compile(r'^(\*{1,6}) +([^\n]+?)(?:\n+|$)')
    list_block = re.compile(
        r'^( *)([+-]|\d+\.) [\s\S]+?'
        r'(?:'
        r'\n+(?=\1?(?:[-*_] *){3,}(?:\n+|$))'
        r'|\n{2,}'
        r'(?! )'
        r'(?!\1(?:[+-]|\d+\.) )\n*'
        r'|'
        r'\s*$)'
    )
    list_item = re.compile(
        r'^(( *)(?:[+-]|\d+\.) [^\n]*'
        r'(?:\n(?!\2(?:[+-]|\d+\.) )[^\n]*)*)',
        flags=re.M
    )
    source = re.compile(
        r'^ *#\+(?:BEGIN_SRC|begin_src) +([\S]*) *\n'
        r'([\s\S]+?)\s*'
        r' *#\+(?:END_SRC|end_src) *(?:\n+|$)'
    )
    html = re.compile(
        _gen_org_re_for_begin_end('html')
    )
    example = re.compile(
        _gen_org_re_for_begin_end('example')
    )
    quote = re.compile(
        _gen_org_re_for_begin_end('quote')
    )
    verse = re.compile(
        _gen_org_re_for_begin_end('verse')
    )
    center = re.compile(
        _gen_org_re_for_begin_end('center')
    )
    paragraph = re.compile(
        r'^((?:[^\n]+\n?(?!'
        r'%s|%s|%s|%s'
        r'))+)\n*' % (
            _pure_pattern(source).replace(r'\1', r'\2'),
            _pure_pattern(list_block).replace(r'\1', r'\3'),
            _pure_pattern(heading),
            _pure_pattern(quote),
        )
    )
    text = re.compile(r'^[^\n]+')


class OrgParser(object):
    default_rule_keys = [
        'newline', 'heading', 'list_block',
        'source', 'html', 'example', 'quote', 'center',
        'paragraph', 'text'
    ]

    def __init__(self, rules=None):
        if rules is not None:
            self.rules = rules
        else:
            self.rules = Rules()
        self.doc_root = BeautifulSoup()

    def parse(self, text, rule_keys=None):
        text = text.rstrip('\n')

        if rule_keys is None:
            rule_keys = self.default_rule_keys
        # for key in rule_keys:
        #     rule = getattr(self.rules, key)
        #     print(rule.pattern)

        def try_parse(text):
            for key in rule_keys:
                rule = getattr(self.rules, key)
                m = rule.match(text)
                if m is None:
                    continue
                getattr(self, 'parse_%s' % key)(m)
                return m
            return None

        while text:
            m = try_parse(text)
            if m is not None:
                text = text[len(m.group(0)):]
                continue
            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)
        return self.doc_root

    def parse_newline(self, m):
        length = len(m.group(0))
        if length > 1:
            new_tag = self.doc_root.new_tag('br')
            self.doc_root.append(new_tag)

    def parse_heading(self, m):
        level = len(m.group(1))
        new_tag = self.doc_root.new_tag('h%d' % (level + 1))
        new_tag.string = m.group(2)
        self.doc_root.append(new_tag)

    def parse_list_block(self, m):
        new_tag = self.doc_root.new_tag('ul')

        cap = self.rules.list_item.findall(m.group(0))

        _next = False
        length = len(cap)

        for i in range(length):
            item = cap[i][0]

            # remove the bullet
            space = len(item)
            # item = self.rules.list_bullet.sub('', item)

            # outdent
            # if '\n ' in item:
            #     space = space - len(item)
            #     pattern = re.compile(r'^ {1,%d}' % (space, flags=re.M)
            #     item = pattern.sub('', item)

            # determine whether item is loose or not
            loose = _next
            if not loose and re.search(r'\n\n(?!\s*$)', item):
                loose = True

            rest = len(item)
            if i != length - 1 and rest:
                _next = item[rest-1] == '\n'
                if not loose:
                    loose = _next

            if loose:
                t = 'loose_item_start'
            else:
                t = 'list_item_start'

            new_li_tag = self.doc_root.new_tag('li')
            new_li_tag.string = item
            new_tag.append(new_li_tag)

        self.doc_root.append(new_tag)

    def parse_source(self, m):
        new_tag = self.doc_root.new_tag('pre')
        new_tag['class'] = 'src src-%s' % m.group(1)
        new_tag.string = m.group(2)
        self.doc_root.append(new_tag)

    def parse_html(self, m):
        new_tag = BeautifulSoup(m.group(1))
        self.doc_root.append(new_tag)

    def parse_example(self, m):
        new_tag = self.doc_root.new_tag('pre')
        new_tag['class'] = 'example'
        new_tag.string = m.group(1)
        self.doc_root.append(new_tag)

    def parse_quote(self, m):
        new_tag = self.doc_root.new_tag('blockquote')
        new_tag.string = m.group(1)
        self.doc_root.append(new_tag)

    def parse_verse(self, m):
        pass

    def parse_center(self, m):
        new_tag = self.doc_root.new_tag('div')
        new_tag.string = m.group(1)
        new_tag['class'] = 'center'
        self.doc_root.append(new_tag)

    def parse_paragraph(self, m):
        new_tag = self.doc_root.new_tag('p')
        new_tag.string = m.group(1).rstrip('\n')
        self.doc_root.append(new_tag)

    def parse_text(self, m):
        new_tag = self.doc_root.new_tag('p')
        new_tag.string = m.group(0)
        self.doc_root.append(new_tag)


class PyOrg(object):
    def __init__(self):
        self.rules = OrgParser

        self.tokens = []

    def __call__(self, text):
        return self.render(text)

    def render(self, text):
        parser = OrgParser()
        soup = parser.parse(text)
        output = soup.prettify()

        return output


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Must have exactly one org file')
    org_filepath = sys.argv[1]

    text = file(org_filepath).read()
    py_org = PyOrg()
    html = py_org.render(text)
    print(text)
    print(html)
