# -*- coding: utf-8 -*-

import sys
from time import time

import redis
import redis.client
from tornado.web import RequestHandler

from doodle.config import CONFIG


def redis_timer(func):
    def wrap(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        duration = end_time - start_time
        frame = sys._getframe(1)
        while frame:
            f_locals = frame.f_locals
            self = f_locals.get('self')
            if self and isinstance(self, RequestHandler):
                if hasattr(self, '_db_time'):
                    self._db_time += duration
                    self._db_count += 1
                else:
                    self._db_time = duration
                    self._db_count = 1
                break
            frame = frame.f_back
        return result
    return wrap


def timer_redis_commends():
    for class_ in (redis.StrictRedis,
                   redis.client.PubSub,
                   redis.client.BasePipeline):
        class_.execute_command = redis_timer(class_.execute_command)


# timer_redis_commends()

redis_main_client = redis.StrictRedis(**CONFIG.REDIS_MAIN_DB)
redis_cache_client = redis.StrictRedis(**CONFIG.REDIS_CACHE_DB)
