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

        if not self.referer:
            raise HTTPError(403)
        match = URL_PATTERN.match(self.referer)
        if not match:
            raise HTTPError(403)
        referer_host = match.group('host')
        if not referer_host:
            raise HTTPError(403)

        host = self.request.headers.get('Host')
        if host != referer_host:
            raise HTTPError(403)

        output = {}
        if self.current_user:
            output['has_logged_in'] = 1
            output['user_name'] = self.current_user.name
            output['logout_url'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'logout'
            output['profile_url'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'profile'
            output['comment_url_prefix'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'comment/'
            extension = '.js' if CONFIG.DEBUG_MODE else '.min.js'
            output['article_js_urls'] = [
                CONFIG.BLOG_HOME_RELATIVE_PATH + 'static/markitup/jquery.markitup' + extension,
                CONFIG.BLOG_HOME_RELATIVE_PATH + 'static/markitup/sets/bbcode/set' + extension,
                CONFIG.BLOG_HOME_RELATIVE_PATH + 'static/theme/null/js/msgbox' + extension
            ]
            if self.is_admin:
                output['is_admin'] = 1
                output['admin_url'] = CONFIG.BLOG_ADMIN_RELATIVE_PATH
                output['edit_url_prefix'] = CONFIG.BLOG_ADMIN_RELATIVE_PATH + 'article/'
        else:
            output['login_url'] = CONFIG.LOGIN_URL

        self.write_json(output)
