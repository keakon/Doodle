# -*- coding: utf-8 -*-

import cgi

from .postmarkup import render_bbcode, _re_html


class ContentFormatFlag(object):
    PLAIN = 0
    BBCODE = 1
    HTML = 2


def convert_bbcode_to_html(bbcode_content, escape=True, exclude_tags=()):
    return render_bbcode(bbcode_content, auto_urls=False, clean=False, exclude_tags=exclude_tags, escape=escape)


def parse_plain_text(content):
    return cgi.escape(content).replace('\n', '<br/>').replace('  ', '&#160;&#160;').replace('\t', '&#160;&#160;&#160;&#160;')


def format_content(content, format):
    if format:
        if format & ContentFormatFlag.BBCODE:
            return convert_bbcode_to_html(content, escape=not(format & ContentFormatFlag.HTML))
        if format & ContentFormatFlag.HTML:
            return content
    return parse_plain_text(content)


def strip_html(content, length):
    result = _re_html.sub(' ', content)
    return result[:length].strip()


def tagattr(name, expr, value=None):
    if not expr:
        return ''
    if value is None:
        value = expr
    return ' %s="%s"' % (name, value)
