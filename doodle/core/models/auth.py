# -*- coding: utf-8 -*-

from base64 import urlsafe_b64encode
from os import urandom
import struct
import time

from redis.exceptions import WatchError

from doodle.config import CONFIG
from doodle.core.redis_client import redis_cache_client

from .base_model import SimpleModel


class Auth(SimpleModel):
    KEY = 'Auth:%s'
    redis_client = redis_cache_client

    @classmethod
    def generate(cls, next_url):
        with cls.redis_client.pipeline(transaction=True) as pipe:
            while True:
                try:
                    state = cls._generate_state()
                    key = cls.KEY % state
                    pipe.watch(key)
                    if pipe.exists(key):
                        pipe.unwatch(key)
                        continue

                    pipe.multi()
                    pipe.set(key, next_url, ex=CONFIG.AUTH_EXPIRE_TIME)
                    pipe.execute()
                except WatchError:
                    continue
                else:
                    return state

    @classmethod
    def _generate_state(cls):
        # 由随机字符串 + 时间戳生成，基本不会碰撞
        return urlsafe_b64encode(urandom(CONFIG.AUTH_RANDOM_BYTES) + struct.pack('<d', time.time()))

    @classmethod
    def get(cls, state):
        # 避免重放攻击，只允许获取一次
        with cls.redis_client.pipeline(transaction=True) as pipe:
            try:
                key = cls.KEY % state
                pipe.watch(key)
                next_url = pipe.get(key)
                pipe.multi()
                pipe.delete(key)
                pipe.execute()
            except WatchError:
                return
            else:
                return next_url
