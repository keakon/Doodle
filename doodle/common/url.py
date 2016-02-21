# -*- coding: utf-8 -*-

import re
from urllib import quote

from doodle.config import CONFIG


URL_PATTERN = re.compile(
    r'''^
    (?:(?:(?P<scheme>https?):)?//  # scheme
    (?P<host>[0-9a-zA-Z\-\.]+(?::\d{1,5})?))?  # host
    (?P<path>/[\w\-\./!~\*\'\(\)%:@&=+\$,]*)?  # path
    (?P<query>\?[\w\-.!~\*\'\(\)%;/\?:@&=+,\$]+)?  # query
    (?P<fragment>\#[\w\-.!~\*\'\(\)%;/\?:@&=+,\$]+)?  # fragment
    $''', re.X)


if CONFIG.REPLACE_SPECIAL_CHARACTERS_FOR_URL:
    def replace_special_characters_for_url(string):
        return CONFIG.URL_SPECIAL_CHARACTERS.sub(CONFIG.URL_REPLACE_CHARACTER, string)
else:
    replace_special_characters_for_url = lambda string: string


def quoted_string(unicode, coding='utf-8'):
    return quote(unicode.encode(coding), '_.-+/=~,;&:!*$()')
