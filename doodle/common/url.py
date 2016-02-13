# -*- coding: utf-8 -*-

from urllib import quote

from doodle.config import CONFIG


if CONFIG.REPLACE_SPECIAL_CHARACTERS_FOR_URL:
    def replace_special_characters_for_url(string):
        return CONFIG.URL_SPECIAL_CHARACTERS.sub(CONFIG.URL_REPLACE_CHARACTER, string)
else:
    replace_special_characters_for_url = lambda string: string


def quoted_string(unicode, coding='utf-8'):
    return quote(unicode.encode(coding), '_.-+/=~,;&:!*$()')
