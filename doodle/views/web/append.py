# -*- coding: utf-8 -*-

import logging
from cgi import escape

from tornado.web import HTTPError

from doodle.common.url import URL_PATTERN
from doodle.config import CONFIG

from ..base_handler import UserHandler


class PageAppendHandler(UserHandler):
    def get(self):
        self.set_cache(CONFIG.DEFAULT_CACHE_TIME, is_public=False)

        page = self.get_argument('page')
        if page not in ('home', 'article', 'category_articles', 'tag_articles', 'search', 'profile'):
            raise HTTPError(404)

        headers = self.request.headers

        referer = headers.get('Referer')
        if not referer:
            raise HTTPError(403)
        match = URL_PATTERN.match(referer)
        if not match:
            raise HTTPError(403)

        host = headers.get('Host')
        if not host:
            raise HTTPError(403)
        if host != match.group(2):
            raise HTTPError(403)

        output = {}
        if self.current_user:
            output['user_id'] = self.current_user_id
            output['logout_url'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'logout'
            if self.is_admin():
                output['is_admin'] = 1
                output['admin_url'] = CONFIG.BLOG_ADMIN_RELATIVE_PATH
            if page == 'article':
                output['append_js_urls'] = [
                    CONFIG.BLOG_HOME_RELATIVE_PATH + 'static/markitup/jquery.markitup.js',
                    CONFIG.BLOG_HOME_RELATIVE_PATH + 'static/markitup/sets/bbcode/set.js',
                    CONFIG.BLOG_HOME_RELATIVE_PATH + 'static/theme/null/js/msgbox.js'
                ]
                output['comment_url_prefix'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'comment/'
                output['profile_url'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'profile'
                output['user_name'] = escape(self.current_user.name)
                if self.is_admin():
                    output['edit_url_prefix'] = CONFIG.BLOG_ADMIN_RELATIVE_PATH + 'article/'
        else:
            output['login_url'] = CONFIG.LOGIN_URL

        self.write_json(output)
