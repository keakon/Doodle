# -*- coding: utf-8 -*-

import logging

from tornado.auth import AuthError, GoogleOAuth2Mixin
from tornado.gen import coroutine
from tornado.web import HTTPError
from tornado.httpclient import HTTPError as HTTPClientError
import json

from doodle.common.url import URL_PATTERN
from doodle.config import CONFIG
from doodle.core.models.auth import Auth
from doodle.core.models.user import User

from ..base_handler import authorized, UserHandler


class LoginHandler(UserHandler, GoogleOAuth2Mixin):
    @coroutine
    def get(self):
        self.set_cache(0, is_public=False)

        if CONFIG.ENABLE_HTTPS and not self.is_https:
            request = self.request
            self.redirect('https://%s%s' % (request.host, request.uri), status=302 if request.version == 'HTTP/1.0' else 303)
            return

        if self.current_user_id:
            self.set_session_time_cookie()  # 强制修改 session_time，使用户可以重新访问 PageAppendHandler，以更新配置信息
            self.redirect(self.get_next_url() or '/')
            return

        code = self.get_argument('code', None)
        if code:
            state = self.get_argument('state')
            if len(state) != CONFIG.AUTH_STATE_LENGTH:
                raise HTTPError(400)
            if self.get_cookie('state') != state:
                raise HTTPError(403)
            next_url = Auth.get(state)
            if next_url is None:
                raise HTTPError(403)
            self.clear_cookie('state')

            try:
                request = self.request
                host = request.host
                if host == CONFIG.MAJOR_DOMAIN:
                    redirect_uri = CONFIG.GOOGLE_OAUTH2_REDIRECT_URI
                else:
                    redirect_uri = '%s://%s%s' % (request.protocol, host, CONFIG.LOGIN_URL)
                token_info = yield self.get_authenticated_user(
                    redirect_uri=redirect_uri,
                    code=code)
                if token_info:
                    access_token = token_info.get('access_token')
                    if access_token:
                        try:
                            response = yield self.get_auth_http_client().fetch('https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + access_token)
                        except HTTPClientError:
                            logging.exception('failed to get user info')
                            raise HTTPError(500)

                        user_info = json.loads(response.body)
                        user = User.get_by_email(user_info['email'])
                        if not user:
                            user = User(
                                email=user_info['email'],
                                name=user_info['name']
                            )
                            url = user_info.get('url')
                            if url:
                                user.site = url
                            user.save(inserting=True)

                        self.set_secure_cookie('user_id', str(user.id), httponly=True, secure=self.is_https)
                        self.set_session_time_cookie()  # 使用户重新访问 PageAppendHandler，以更新配置信息
                        self.redirect(next_url or '/')
                        return
            except AuthError:
                logging.warning('failed to login', exc_info=True)
            raise HTTPError(403)
        else:
            state = self.get_cookie('state')
            if not (state and Auth.is_existing(state)):  # invalid state
                state = Auth.generate(self.get_next_url() or '')
                self.set_state_cookie(state)
            request = self.request
            host = request.host
            if host == CONFIG.MAJOR_DOMAIN:
                redirect_uri = CONFIG.GOOGLE_OAUTH2_REDIRECT_URI
            else:
                redirect_uri = '%s://%s%s' % (request.protocol, host, CONFIG.LOGIN_URL)
            yield self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=CONFIG.GOOGLE_OAUTH2_CLIENT_ID,
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto', 'state': state})


class LogoutHandler(UserHandler):
    def get(self):
        self.set_cache(0, is_public=False)
        self.set_session_time_cookie()  # 强制修改 session_time，使用户可以重新访问 PageAppendHandler，以更新配置信息
        if self.referer:
            match = URL_PATTERN.match(self.referer)
            if match:
                request = self.request
                if match.group('host') == request.host and match.group('scheme') == request.protocol:
                    if self.current_user_id:
                        self.clear_cookie('user_id')
                    self.redirect(match.group('path'))
                    return
        self.redirect('/')


class ProfileHandler(UserHandler):
    @authorized()
    def get(self):
        self.render('web/profile.html', {
            'title': '账号设置',
            'page': 'profile'
        })

    @authorized()
    def post(self):
        current_user = self.current_user
        name = self.get_argument('name')
        if name and len(name) <= 15 and current_user.name != name:
            current_user.name = name
            self.set_session_time_cookie()

        site = self.get_argument('site')
        if site:
            match = URL_PATTERN.match(site)
            if match:
                if not match.group('host'):
                    self.finish('抱歉，您填的网址不正确')
                    return
                if not match.group('scheme'):
                    site = 'http://' + site
                current_user.site = site
            else:
                self.finish('抱歉，您填的网址不正确')
                return
        else:
            current_user.site = None
        current_user.save()
        self.finish('您的资料保存成功了')
