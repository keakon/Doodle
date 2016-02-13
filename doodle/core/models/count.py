# -*- coding: utf-8 -*-

from .base_model import SimpleModel


class Count(SimpleModel):
    @classmethod
    def increase(cls, id, count=1):
        return cls.redis_client.hincrby(cls.KEY, id, count)

    @classmethod
    def decrease(cls, id, count=1):
        return cls.redis_client.hincrby(cls.KEY, id, -count)

    @classmethod
    def get(cls, id):
        count = cls.redis_client.hget(cls.KEY, id)
        return int(count) if count else 0

    @classmethod
    def get_by_ids(cls, ids):
        counts = cls.redis_client.hmget(cls.KEY, ids)
        count_zip = zip(ids, [int(count) for count in counts])
        return dict(count_zip)

    @classmethod
    def set(cls, id, count):
        if count:
            cls.redis_client.hset(cls.KEY, id, count)
        else:
            cls.redis_client.hdel(cls.KEY, id)

    @classmethod
    def get_by_ids(cls, ids):
        if ids:
            counts = cls.redis_client.hmget(cls.KEY, ids)
            return dict(zip(ids, counts))
        return {}
