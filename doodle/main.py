# -*- coding: utf-8 -*-

from doodle.common.logger import log_request  # should be first statement to init logging

import socket
import sys

import tornado.httpclient
import tornado.ioloop
import tornado.netutil
import tornado.web

from doodle.common.http_server import HTTPServer
from doodle.config import CONFIG
from doodle.views.urls import handlers


def get_application():
    tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

    app = tornado.web.Application(
        handlers,
        debug=CONFIG.DEBUG_MODE,
        cookie_secret=CONFIG.COOKIE_SECRET,
        xsrf_cookies=CONFIG.XSRF_COOKIES,
        gzip=CONFIG.GZIP,
        template_path=CONFIG.TEMPLATE_PATH,
        static_path=CONFIG.STATIC_PATH,
        login_url=CONFIG.LOGIN_URL,
        log_function=log_request,
        google_oauth={
            'key': CONFIG.GOOGLE_OAUTH2_CLIENT_ID,
            'secret': CONFIG.GOOGLE_OAUTH2_CLIENT_SECRET
        }
    )

    return app


def get_port():
    if len(sys.argv) >= 2:
        port = sys.argv[1]
        if port.isdigit():
            port = int(port)
            if port < 65535:
                return port
    return CONFIG.PORT


def main():
    application = get_application()
    port = get_port()

    if CONFIG.IPV4_ONLY:
        family = socket.AF_INET
    else:
        family = socket.AF_UNSPEC

    sockets = tornado.netutil.bind_sockets(port, CONFIG.HOST, family=family)
    server = HTTPServer(application, xheaders=CONFIG.XHEADERS)
    server.add_sockets(sockets)
    server.listen_exit_signal(CONFIG.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
