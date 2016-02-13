# -*- coding: utf-8 -*-

from .default import Config


class TestConfig(Config):
    # application config
    TEST = True

    # redis config
    REDIS_MAIN_DB = {'host': 'localhost', 'port': 6379, 'db': 10}
    REDIS_CACHE_DB = {'host': 'localhost', 'port': 6379, 'db': 11}
