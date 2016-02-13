# -*- coding: utf-8 -*-

import logging
import signal
import time

import tornado.httpserver
import tornado.ioloop


class HTTPServer(tornado.httpserver.HTTPServer):
    def __init__(self, *args, **kwargs):
        super(HTTPServer, self).__init__(*args, **kwargs)
        self._shutting_down = False
        self._listening_exit_signal = False

    def safe_shutdown(self, timeout):
        if self._shutting_down:
            return

        self._shutting_down = True
        logging.debug('Stopping http server.')
        self.stop()

        logging.debug('Will be shutdown within %s seconds ...', timeout)
        io_loop = tornado.ioloop.IOLoop.instance()

        deadline = time.time() + timeout

        def safe_stop_loop():
            now = time.time()
            if now < deadline and io_loop._callbacks:
                io_loop.add_timeout(now + 1, safe_stop_loop)
            else:
                io_loop.stop()
                logging.debug('Http server has been shutdown.')
        safe_stop_loop()

    def listen_exit_signal(self, timeout):
        if self._listening_exit_signal:
            return

        def handle_exit_signal(sig, frame):
            logging.warning('Caught signal: %s', sig)
            tornado.ioloop.IOLoop.instance().add_callback_from_signal(self.safe_shutdown, timeout)

        signal.signal(signal.SIGTERM, handle_exit_signal)
        signal.signal(signal.SIGINT, handle_exit_signal)
