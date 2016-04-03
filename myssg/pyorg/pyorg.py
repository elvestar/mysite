# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import re

from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
import pangu


def _pure_pattern(regex):
    pattern = regex.pattern
    if pattern.startswith('^'):
        pattern = pattern[1:]
    return pattern

_emphasis_symbols = '\*=_/+~'


class Rules(object):
    # Block rules
    newline = re.compile(r'^\n+')
    heading = re.compile(r'^(\*{1,6}) +([^\n]+?)(?:\n+|$)')
    list_block = re.compile(
        r'^( *)([+-]|\d+\.) [\s\S]+?'
        r'(?:'
        r'\n+(?=\1?(?:[-*_] *){3,}(?:\n+|$))'
        r'|\n{2,}(?! )(?!\1(?:[+-]|\d+\.) )\n*'
        r'|\n+(?=[^ +\-\d])'
        r'|\s*$'
        r')'
    )
    list_item = re.compile(
        r'^(( *)([+-]|\d+\.) ([^\n]*'
        r'(?:\n(?!\2(?:[+-]|\d+\.) )[^\n]*)*))',
        flags=re.M
    )
    table = re.compile(
        r'^ *\|(.+)\n'
        r'*\|( *[-]+[-| +]*)\n'
        r'((?: *\|.*(?:\n|$))*)\n*'
    )
    empty_table_row = re.compile(
        r'^[| ]+$'
    )
    source = re.compile(
        r'^ *#\+(?:BEGIN_SRC|begin_src) +([\S]*) *\n'
        r'([\s\S]+?)\s*'
        r' *#\+(?:END_SRC|end_src)\s*(?:\n+|$)'
    )
    begin_xxx = re.compile(
        r'^ *#\+(?:BEGIN_|begin_)'
        r'(html|HTML|example|EXAMPLE|quote|QUOTE|verse|VERSE|center|CENTER) *\n'
        r'([\s\S]+?)\s*'
        r' *#\+(?:END_|end_)\1\s*(?:\n+|$)'
    )
    paragraph = re.compile(
        r'^((?:[^\n]+\n?(?!'
        r'%s|%s|%s|%s|%s'
        r'))+)\n*' % (
            _pure_pattern(source).replace(r'\1', r'\2'),
            _pure_pattern(begin_xxx).replace(r'\1', r'\4'),
            _pure_pattern(list_block).replace(r'\1', r'\5'),
            _pure_pattern(heading),
            _pure_pattern(table),
        )
    )
    text = re.compile(r'^[^\n]+')

    # Inline rules
    escape = re.compile(r'^\\([\\`*{}\[\]()#+\-.!_>~|])')  # \* \+ \! ....
    link = re.compile(
        r'^\['
        r'\[([^\]]+)\]'
        r'(\[([^\]]+)\])?'
        r'\]'
    )
    url = re.compile(r'''^(https?:\/\/[^\s<]+[^<.,:;"')\]\s])''')
    emphasis = re.compile(
        r'^ ([%s])(\S[\s\S]+?)(?:\1 |\1$)' % _emphasis_symbols
    )
    emphasis_in_start = re.compile(
        r'^ ?([%s])(\S[\s\S]+?)(?:\1 |\1$)' % _emphasis_symbols
    )
    footnote = re.compile(r'^\[\^([^\]]+)\]')
    inline_text = re.compile(
        r'^[\s\S]+?(?= [%s]|https?://| {2,}\n|$)' % _emphasis_symbols
    )


class OrgParser(object):
    block_rule_keys = [
        'newline', 'heading', 'list_block', 'table',
        'source', 'begin_xxx',
        'paragraph', 'text'
    ]
    inline_rule_keys = [
        'url',
        'link', 'emphasis_in_start',
        'inline_text',
        ]
    # inline_rule_keys = [
    #     'escape', 'autolink', 'url',
    #     'footnote', 'link', 'reflink', 'nolink',
    #     'emphasis', 'code',
    #     'linebreak', 'strikethrough', 'inline_text',
    #     ]

    def __init__(self, rules=None):
        if rules is not None:
            self.rules = rules
        else:
            self.rules = Rules()
        self.doc_root = BeautifulSoup()
        self.heading_count = 0

    def parse(self, text, block_rule_keys=None, inline_rule_keys=None):
        text = text.rstrip('\n')

        if block_rule_keys is not None:
            self.block_rule_keys = block_rule_keys
        if inline_rule_keys is not None:
            self.inline_rule_keys = inline_rule_keys

        return self.parse_by_block_rules(text, self.doc_root)

    def parse_by_block_rules(self, text, root=None):
        return self.parse_by_rules(text, self.block_rule_keys, root)

    def parse_by_inline_rules(self, text, root=None):
        return self.parse_by_rules(text, self.inline_rule_keys, root)

    def parse_by_rules(self, text, rule_keys, root=None):
        if root is None:
            root = self.doc_root
        in_text_start = True
        self.switch_rules(rule_keys, in_text_start)
        while text:
            m = None
            for key in rule_keys:
                rule = getattr(self.rules, key)
                m = rule.match(text)
                if m is None:
                    continue
                getattr(self, 'parse_%s' % key)(m, root)
                break
            if m is not None:
                text = text[len(m.group(0)):]
                if in_text_start:
                    in_text_start = False
                    self.switch_rules(rule_keys, in_text_start)
                continue
            if text is not None:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)
        return root

    @staticmethod
    def switch_rules(rule_keys, in_text_start):
        """ For some elements, parse rules depends whether they are in text start.

        For example, for emphasis element(bold, italic, ...), if it is in text start,
        there is not necessary a space before the emphasis symbol(*, /, ...).
        """
        rule_keys_map = {
            'emphasis': 'emphasis_in_start',
        }
        if not in_text_start:
            rule_keys_map = dict((v, k) for k, v in rule_keys_map.items())
        for k, v in rule_keys_map.items():
            if k in rule_keys:
                index = rule_keys.index(k)
                rule_keys[index] = v

    def parse_newline(self, m, root):
        length = len(m.group(0))
        if length > 1:
            new_tag = root.new_tag('br')
            root.append(new_tag)

    def parse_heading(self, m, root):
        level = len(m.group(1)) + 1
        new_tag = root.new_tag('h%d' % level)
        self.heading_count += 1
        new_tag['id'] = 'sec-%d' % self.heading_count
        self.parse_by_inline_rules(m.group(2), new_tag)
        root.append(new_tag)

    def parse_list_block(self, m, root):
        new_tag = None

        cap = self.rules.list_item.findall(m.group(0))

        length = len(cap)
        for i in range(length):
            bullet = cap[i][2]
            item_content = cap[i][3]
            if new_tag is None:
                if bullet in ['+', '-']:
                    new_tag = root.new_tag('ul')
                else:
                    new_tag = root.new_tag('ol')

            new_li_tag = root.new_tag('li')
            self.parse_by_inline_rules(item_content, new_li_tag)
            new_tag.append(new_li_tag)

        root.append(new_tag)

    def parse_table(self, m, root):
        new_tag = root.new_tag('table')
        # new_tag['class'] = 'table table-bordered'

        thead_str = re.sub(r'^ *| *\| *$', '', m.group(1))
        new_tr_tag = root.new_tag('tr')
        for th_str in re.split(r' *\| *', thead_str):
            new_th_tag = root.new_tag('th')
            self.parse_by_inline_rules(th_str, new_th_tag)
            new_tr_tag.append(new_th_tag)
        new_thead_tag = root.new_tag('thead')
        new_thead_tag.append(new_tr_tag)
        new_tag.append(new_thead_tag)

        new_tbody_tag = root.new_tag('tbody')
        tbody_str = re.sub(r'(?: *\| *)?\n$', '', m.group(3))
        tbody_row_strs = tbody_str.split('\n')
        # Remove empty row in table end first
        for tbody_row_str in reversed(tbody_row_strs):
            if self.rules.empty_table_row.match(tbody_row_str):
                tbody_row_strs.remove(tbody_row_str)
        for tbody_row_str in tbody_row_strs:
            tbody_row_str = re.sub(r'^ *\| *| *\| *$', '', tbody_row_str)
            new_tr_tag = root.new_tag('tr')
            for td_str in re.split(r' *\| *', tbody_row_str):
                new_td_tag = root.new_tag('td')
                self.parse_by_inline_rules(td_str, new_td_tag)
                new_tr_tag.append(new_td_tag)
            new_tbody_tag.append(new_tr_tag)
        new_tag.append(new_tbody_tag)

        root.append(new_tag)

    def parse_source(self, m, root):
        lang = m.group(1)
        formatter = get_formatter_by_name('html', cssclass='codehilite')
        try:
            lexer = get_lexer_by_name(lang)
        except ValueError:
            lexer = get_lexer_by_name('text')
        result = highlight(m.group(2), lexer, formatter)

        new_tag = self.doc_root.new_tag('div')
        new_tag['class'] = 'src src-%s' % lang
        new_tag.append(BeautifulSoup(result))
        root.append(new_tag)

    def parse_begin_xxx(self, m, root):
        symbol = m.group(1)
        if symbol in ['html', 'HTML']:
            new_tag = BeautifulSoup(m.group(2))
        elif symbol in ['example', 'EXAMPLE']:
            new_tag = root.new_tag('pre')
            new_tag['class'] =  'example'
            new_tag.string = m.group(2)
        elif symbol in ['quote', 'QUOTE']:
            new_tag = root.new_tag('blockquote')
            new_tag.string = m.group(2)
        elif symbol in ['verse', 'VERSE']:
            new_tag = root.new_tag('p')
            new_tag['class'] = 'verse'
            new_tag.string = m.group(2)
        elif symbol in ['center', 'CENTER']:
            new_tag = root.new_tag('div')
            new_tag['class'] = 'center'
            new_tag.string = m.group(2)
        else:
            raise RuntimeError('Not supportted begin symbol: %s' % symbol)

        root.append(new_tag)

    def parse_paragraph(self, m, root):
        new_tag = root.new_tag('p')
        content = m.group(1).rstrip('\n')
        self.parse_by_inline_rules(content, new_tag)
        root.append(new_tag)

    def parse_text(self, m, root):
        new_tag = root.new_tag('p')
        new_tag.string = m.group(0)
        root.append(new_tag)

    def parse_link(self, m, root):
        new_tag = self.doc_root.new_tag('a')
        new_tag['href'] = m.group(1)
        new_tag['target'] = '_blank'
        if m.group(2) is None:
            new_tag.string = m.group(1)
        else:
            new_tag.string = m.group(3)
        root.append(new_tag)

    def parse_url(self, m, root):
        new_tag = self.doc_root.new_tag('a')
        new_tag['href'] = m.group(1)
        new_tag['target'] = '_blank'
        new_tag.string = m.group(1)
        root.append(new_tag)

    def parse_emphasis(self, m, root):
        symbol = m.group(1)
        if symbol == '*':
            tag_name = 'b'
        elif symbol == '/':
            tag_name = 'i'
        elif symbol == '_':
            tag_name = 'span'
        elif symbol in ['~', '=']:
            tag_name = 'code'
        elif symbol == '+':
            tag_name = 'del'
        else:
            raise RuntimeError('Not supportted emhpasis symbol: %s' % symbol)
        new_tag = self.doc_root.new_tag(tag_name)
        new_tag.string = m.group(2)
        if symbol == '_':
            new_tag['class'] = 'underline'
        root.append(new_tag)

    def parse_emphasis_in_start(self, m, root):
        return self.parse_emphasis(m, root)

    def parse_inline_text(self, m, root):
        content = m.group(0).replace('\n', '')
        root.append(pangu.spacing(content))


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
