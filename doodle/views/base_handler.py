# -*- coding: utf-8 -*-

from functools import wraps
import re
import time

import pybloof
import tenjin
from tenjin.helpers import escape, to_str, _decode_params, fragment_cache
from tornado.web import Finish, HTTPError, RequestHandler, StaticFileHandler
from tornado.util import bytes_type, unicode_type
import ujson

from doodle.common.property import CachedProperty
from doodle.common.url import URL_PATTERN
from doodle.config import CONFIG
from doodle.core.models.fragment_cache import FragmentCache
from doodle.core.models.auth import Auth
from doodle.core.models.user import User


if CONFIG.DEBUG_MODE:
    Engine = tenjin.Engine
else:
    class Engine(tenjin.Engine):
        def _get_template_from_cache(self, cachepath, filepath):
            # skip file time checking
            return self.cache.get(cachepath, self.templateclass)

fragment_cache.store = FragmentCache
engine = Engine(path=[CONFIG.TEMPLATE_PATH], cache=tenjin.MemoryCacheStorage(), preprocess=True)

TEMPLATE_GLOBALS = {
    'to_str': to_str,
    'escape': escape,
    '_decode_params': _decode_params,
    'CONFIG': CONFIG
}

MIME_TYPE_ABBREVIATIONS = {
    'atom': 'application/atom+xml',
    'html': 'text/html',
    'json': 'application/json',
    'plain': 'text/plain',
    'rss': 'application/rss+xml'
}


class BaseHandler(RequestHandler):
    _SPIDER_PATTERN = re.compile('(bot|crawl|spider|curl|apachebench|slurp|sohu-search|lycos|robozilla)', re.I)
    _CSS_PATTERN = re.compile(r'<link rel="stylesheet" href="(/[\w\-./]+\.css)">')
    _JS_PATTERN = re.compile(r'<script src="(/[\w\-./]+\.js)"></script>')

    def head(self, *args, **kwargs):
        self.get(*args, **kwargs)

    def set_content_type(self, mime_type='text/html', charset='UTF-8'):
        mime_type = MIME_TYPE_ABBREVIATIONS.get(mime_type, mime_type)
        self.set_header('Content-Type', '%s; charset=%s' %
                        (mime_type, charset) if charset else mime_type)

    def set_cache(self, seconds=None, is_public=None, must_revalidate=False):
        parts = []
        if is_public:
            parts.append('public')
        elif is_public is not None:
            parts.append('private')

        if seconds is not None:
            if seconds <= 0:
                self.set_header('Pragma', 'no-cache')
                parts.append('no-cache')
            else:
                parts.append('max-age=%d' % seconds)

        if must_revalidate:
            parts.append('must-revalidate')

        if parts:
            self.set_header('Cache-Control', ', '.join(parts))

    @CachedProperty
    def referer(self):
        return self.request.headers.get('Referer') or ''

    @CachedProperty
    def user_agent(self):
        return self.request.headers.get('User-Agent') or ''

    @CachedProperty
    def is_https(self):
        return self.request.protocol == 'https'

    @CachedProperty
    def is_xhr(self):
        requested_with = self.request.headers.get('X-Requested-With', '')
        return requested_with.lower() == 'xmlhttprequest'

    @CachedProperty
    def is_spider(self):
        if self.user_agent:
            return self._SPIDER_PATTERN.search(self.user_agent) is not None
        return False

    @CachedProperty
    def is_mobile(self):
        headers = self.request.headers
        if 'x-wap-profile' in headers or 'Profile' in headers or 'X-OperaMini-Features' in headers:
            return True

        user_agent = self.user_agent
        if user_agent:
            user_agent_lower = user_agent.lower()
            if 'phone' in user_agent_lower or 'mobi' in user_agent_lower or 'wap' in user_agent_lower:
                return True

            browser, platform, os, os_version, vendor = self.ua_details
            if platform or vendor:
                return True
            if 'is_mobile' in self.__dict__:
                return self.__dict__['is_mobile']

        return False

    @CachedProperty
    def ua_details(self):
        """
        parse browser, platform, os and vendor from user agent.

        从user agent解析浏览器、平台、操作系统和产商信息。

        @rtype: string
        @return: tuple of browser, platform, os, os_version and vendor

        browser, platform, os, os_version, vendor组成的元组
        """
        user_agent = self.user_agent
        os = ''
        os_version = ''
        browser = ''
        platform = ''
        vendor = ''
        if user_agent:
            if 'iPad' in user_agent:
                os = 'iOS'
                platform = 'iPad'
                vendor = 'Apple'
            elif 'iPod' in user_agent:
                os = 'iOS'
                platform = 'iPod Touch'
                vendor = 'Apple'
            elif 'iPhone' in user_agent:
                os = 'iOS'
                platform = 'iPhone'
                vendor = 'Apple'
            elif 'Android' in user_agent:
                os = platform = 'Android'
            elif 'BlackBerry' in user_agent:
                os = 'BlackBerry OS'
                platform = 'BlackBerry'
                vendor = 'RIM'
            elif 'Palm' in user_agent:
                os = 'webOS'
                platform = 'Palm'
            elif 'Windows Phone' in user_agent:
                os = 'Windows CE'
                platform = 'Windows Phone'
            elif 'PSP' in user_agent:
                platform = 'PSP'
                vendor = 'Sony'
            elif 'Kindle' in user_agent:
                os = 'Linux'
                platform = 'Kindle'
            elif 'Nintendo' in user_agent or 'Nitro' in user_agent:
                platform = 'Wii'
                vendor = 'Nintendo'

            if not os:
                if 'Windows' in user_agent:
                    os = 'Windows'
                    if 'Windows NT 6.1' in user_agent:
                        os_version = 'Windows 7'
                    elif 'Windows NT 5.1' in user_agent:
                        os_version = 'Windows XP'
                    elif 'Windows NT 6.0' in user_agent:
                        os_version = 'Windows Vista'
                    elif 'Windows NT 5.2' in user_agent:
                        os_version = 'Windows Server 2003'
                    elif 'Windows NT 5.0' in user_agent:
                        os_version = 'Windows 2000'
                    elif 'Windows CE' in user_agent:
                        os_version = 'Windows CE'
                elif 'Macintosh' in user_agent or 'Mac OS' in user_agent:
                    os = 'Mac OS'
                    if 'Mac OS X' in user_agent:
                        os_version = 'Mac OS X'
                elif 'Linux' in user_agent:
                    os = 'Linux'
                elif 'FreeBSD' in user_agent:
                    os = 'FreeBSD'
                elif 'OpenBSD' in user_agent:
                    os = 'OpenBSD'
                elif 'Solaris' in user_agent:
                    os = 'Solaris'
                elif 'Symbian' in user_agent or 'SymbOS' in user_agent:
                    os = 'SymbianOS'
                    self.is_mobile = True
                    if 'Series60' in user_agent or 'S60' in user_agent:
                        os_version = 'SymbianOS Series60'
                    elif 'Series40' in user_agent or 'S40' in user_agent:
                        os_version = 'SymbianOS Series40'

            if not browser:
                if 'MSIE' in user_agent:
                    browser = 'Internet Explorer'
                elif 'Firefox' in user_agent:
                    browser = 'Firefox'
                elif 'Chrome' in user_agent:
                    browser = 'Chrome'
                elif 'Safari' in user_agent:
                    if 'Mobile' in user_agent:
                        browser = 'Mobile Safari'
                        self.is_mobile = True
                    else:
                        browser = 'Safari'
                elif 'Opera Mini' in user_agent:
                    browser = 'Opera Mini'
                    self.is_mobile = True
                elif 'Opera Mobi' in user_agent:
                    browser = 'Opera Mobile'
                    self.is_mobile = True
                elif 'Opera' in user_agent:
                    browser = 'Opera'
                elif 'UCWEB' in user_agent:
                    browser = 'UCWEB'
                    self.is_mobile = True
                elif 'IEMobile' in user_agent:
                    browser = 'IEMobile'
                    self.is_mobile = True

            if not vendor:
                if 'Nokia' in user_agent:
                    vendor = 'Nokia'
                elif 'motorola' in user_agent:
                    vendor = 'Motorola'
                elif 'Sony' in user_agent:
                    vendor = 'Sony'
                elif 'samsung' in user_agent.lower():
                    vendor = 'Samsung'
        return browser, platform, os, os_version, vendor

    @CachedProperty
    def cursor(self):
        cursor = self.get_argument('cursor', None)
        if cursor:
            try:
                cursor = int(cursor)
            except ValueError:
                self.redirect(self.request.path, permanent=True)
                raise Finish()
            if cursor < 0:
                raise HTTPError(404)
        else:
            cursor = None
        return cursor

    def write_json(self, value, ensure_ascii=False):
        self.finish(ujson.dumps(value, ensure_ascii=ensure_ascii))

    def render(self, template_name, context=None, globals=None, layout=False):
        if context is None:
            context = {'self': self}
        else:
            context['self'] = self
        if globals is None:
            globals = TEMPLATE_GLOBALS
        else:
            globals.update(TEMPLATE_GLOBALS)
        output = engine.render(template_name, context, globals, layout)
        self.push_resources(output)
        self.finish(output)

    def push_resources(self, output):
        if self.request.headers.get('X-Server-Protocol') != 'HTTP/2.0':
            return

        css_list = self._CSS_PATTERN.findall(output)
        js_list = self._JS_PATTERN.findall(output)
        if css_list or js_list:
            filter = None
            filter_was_empty = True
            resources_cookie = self.get_cookie('resources')
            if resources_cookie:
                try:
                    filter = pybloof.StringBloomFilter.from_base64(resources_cookie)
                except Exception:
                    pass
                else:
                    filter_was_empty = False
            if not filter:
                filter = pybloof.StringBloomFilter(size=120, hashes=3)
            if filter_was_empty:
                new_css_list = css_list
                new_js_list = js_list
            else:
                new_css_list = [css for css in css_list if css not in filter]
                new_js_list = [js for js in js_list if js not in filter]
                if not (new_css_list or new_js_list):
                    return
            for css in new_css_list:
                filter.add(css)
            for js in new_js_list:
                filter.add(js)
            self.set_cookie('resources', filter.to_base64())
            self.set_header('Link', ', '.join(['<%s>; as=style; rel=preload' % css for css in new_css_list] + ['<%s>; as=script; rel=preload' % js for js in new_js_list]))

    def decode_argument(self, value, name=None):
        if value is None or isinstance(value, unicode_type):
            return value
        if not isinstance(value, bytes_type):
            raise TypeError(
                "Expected bytes, unicode, or None; got %r" % type(value)
            )
        return unicode(value, 'utf-8', 'replace')


class UserHandler(BaseHandler):
    @CachedProperty
    def current_user_id(self):
        if CONFIG.COOKIE_SECRET:
            user_id = self.get_secure_cookie('user_id', min_version=2)
            if user_id:
                return int(user_id)

    def get_current_user(self):
        user_id = self.current_user_id
        if user_id:
            return User.get_by_id(user_id)

    @CachedProperty
    def is_admin(self):
        return self.current_user_id == CONFIG.ADMIN_USER_ID

    def get_next_url(self):
        if self.referer:
            match = URL_PATTERN.match(self.referer)
            if match and match.group('host') == self.request.host:  # todo: check scheme?
                next_url = match.group('path')
                if next_url and next_url != '/':
                    return next_url

    def set_state_cookie(self, state):
        self.set_cookie('state', state, expires=int(time.time()) + CONFIG.AUTH_EXPIRE_TIME, httponly=True, secure=self.is_https)

    def set_session_time_cookie(self):
        self.set_cookie('session_time', str(int(time.time())), expires_days=30)


class AdminHandler(UserHandler):
    def prepare(self):
        super(AdminHandler, self).prepare()
        self.set_cache(is_public=False)

        if CONFIG.ENABLE_HTTPS and not self.is_https:
            request = self.request
            if request.version == 'HTTP/1.0':
                if request.method in ('GET', 'HEAD'):
                    self.redirect('https://%s%s' % (request.host, request.uri))
                else:
                    raise HTTPError(403)
            else:
                self.redirect('https://%s%s' % (request.host, request.uri), status=307)
            return

        if not self.is_admin:
            if not self.current_user_id:
                request = self.request
                if request.method in ('GET', 'HEAD'):
                    state = Auth.generate(request.uri)
                    self.set_state_cookie(state)
                    self.redirect(self.get_login_url(), status=302 if request.version == 'HTTP/1.0' else 303)
                    return
                self.set_session_time_cookie()  # force check user status
            raise HTTPError(403)


class NotFoundHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.set_cache(CONFIG.DEFAULT_CACHE_TIME, True)
        self.send_error(404)


class BlankPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.set_status(204)

    post = get


class StaticFileHandler(StaticFileHandler):
    def get_cache_time(self, path, modified, mime_type):
        return self.CACHE_MAX_AGE if 'v' in self.request.arguments else 60 * 60 * 24 * 30


def authorized(admin_only=False):
    def wrap(user_handler):
        @wraps(user_handler)
        def authorized_handler(self, *args, **kwargs):
            self.set_cache(is_public=False)
            request = self.request
            if request.method == 'GET':
                if not self.current_user_id:
                    state = Auth.generate(request.uri)
                    self.set_state_cookie(state)
                    self.redirect(self.get_login_url(), status=302 if request.version == 'HTTP/1.0' else 303)
                elif admin_only and not self.is_admin:
                    raise HTTPError(403)
                else:
                    user_handler(self, *args, **kwargs)
            elif not self.current_user_id:
                self.set_session_time_cookie()  # force check user status
                raise HTTPError(403)
            elif admin_only and not self.is_admin:
                raise HTTPError(403)
            else:
                user_handler(self, *args, **kwargs)
        return authorized_handler
    return wrap
