# -*- coding: utf-8 -*-

from .base_model import SimpleModel


class MaxID(SimpleModel):
    @classmethod
    def get_next_id(cls, for_type, increment=1):
        return cls.redis_client.hincrby(cls.KEY, for_type, increment)

    @classmethod
    def get_max_id(cls, for_type):
        return int(cls.redis_client.hget(cls.KEY, for_type) or 0)
