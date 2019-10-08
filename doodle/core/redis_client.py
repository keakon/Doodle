# -*- coding: utf-8 -*-

import redis

from doodle.config import CONFIG


redis_main_client = redis.Redis(**CONFIG.REDIS_MAIN_DB)
redis_cache_client = redis.Redis(**CONFIG.REDIS_CACHE_DB)
