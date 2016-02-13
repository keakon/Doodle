# -*- coding: utf-8 -*-

from doodle.core.redis_client import redis_cache_client


class FragmentCache(object):
    KEY = 'fragment_cache:%s'

    @classmethod
    def get(cls, key):
        return redis_cache_client.get(cls.KEY % key)

    @classmethod
    def set(cls, key, value, lifetime=0):
        redis_cache_client.set(cls.KEY % key, value, ex=lifetime)
        return True

    @classmethod
    def delete(cls, key):
        return redis_cache_client.delete(cls.KEY % key) == 1

    @classmethod
    def has(cls, key):
        return redis_cache_client.exists(cls.KEY % key)
