# -*- coding: utf-8 -*-

from .default import Config


class ProductionConfig(Config):
    # application config
    DEBUG_MODE = False
    GZIP = False  # 应该用 nginx 来压缩

    # redis config
    REDIS_MAIN_DB = {'unix_socket_path': '/tmp/doodle_redis_main.sock'}
    REDIS_CACHE_DB = {'unix_socket_path': '/tmp/doodle_redis_cache.sock'}
