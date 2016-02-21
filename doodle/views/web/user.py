# -*- coding: utf-8 -*-

import time

from tornado.auth import AuthError, GoogleOAuth2Mixin
from tornado.gen import coroutine
from tornado.web import HTTPError
from tornado.httpclient import HTTPError as HTTPClientError
import ujson

from doodle.common.url import URL_PATTERN
from doodle.config import CONFIG
from doodle.core.models.auth import Auth
from doodle.core.models.user import User

from ..base_handler import authorized, UserHandler


class LoginHandler(UserHandler, GoogleOAuth2Mixin):
    @coroutine
    def get(self):
        self.set_cache(0, is_public=False)

        if self.current_user_id:
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
                token_info = yield self.get_authenticated_user(
                    redirect_uri=CONFIG.GOOGLE_OAUTH2_REDIRECT_URI,
                    code=code)
                if token_info:
                    access_token = token_info.get('access_token')
                    if access_token:
                        try:
                            response = yield self.get_auth_http_client().fetch('https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + access_token)
                        except HTTPClientError:
                            raise HTTPError(500)

                        user_info = ujson.loads(response.body)
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

                        self.set_secure_cookie('user_id', str(user.id))
                        self.set_cookie('session_time', str(int(time.time())), expires_days=30)
                        self.redirect(next_url or '/')
                        return
            except AuthError:
                pass
            raise HTTPError(403)
        else:
            state = self.get_cookie('state')
            if not (state and Auth.is_existing(state)):  # invalid state
                state = Auth.generate(self.get_next_url() or '')
                self.set_cookie('state', state, expires=int(time.time()) + CONFIG.AUTH_EXPIRE_TIME, httponly=True, secure=self.is_https)
            yield self.authorize_redirect(
                redirect_uri=CONFIG.GOOGLE_OAUTH2_REDIRECT_URI,
                client_id=CONFIG.GOOGLE_OAUTH2_CLIENT_ID,
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto', 'state': state})


class LogoutHandler(UserHandler):
    def get(self):
        self.set_cache(0, is_public=False)
        if self.referer:
            match = URL_PATTERN.match(self.referer)
            if match:
                request = self.request
                if match.group('host') == request.host and match.group('scheme') == request.protocol:
                    if self.current_user_id:
                        self.clear_cookie('user_id')
                        self.set_cookie('session_time', str(int(time.time())), expires_days=30)
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
        if name and len(name) < 15:
            current_user.name = name

        site = self.get_argument('site')
        if site:
            if site[:4] == 'www.':
                site = 'http://' + site
            current_user.site = site
        else:
            current_user.site = None
        current_user.save()
        self.finish('您的资料保存成功了')

    def compute_etag(self):
        return
