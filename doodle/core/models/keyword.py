# -*- coding: utf-8 -*-

import logging

from doodle.config import CONFIG
from doodle.core.property import IntegerProperty, StringProperty
from doodle.core.redis_client import redis_cache_client

from .base_model import JSONModel


class KeywordArticle(JSONModel):
    keywords = StringProperty()
    article_id = IntegerProperty()

    def _get_watching_keys(self, inserting=False):
        return [self.KEY]

    def _save_self(self, redis_client, inserting=False):
        member = '%s:%d' % (self.keywords, self.article_id)
        redis_client.sadd(self.KEY, member)

    def delete(self, redis_client):
        member = '%s:%d' % (self.keywords, self.article_id)
        redis_client.srem(self.KEY, member)

    @classmethod
    def query_by_keyword(cls, keyword, result_limit=CONFIG.SEARCH_PAGE_SIZE, search_limit=CONFIG.MAX_SEARCH_COUNT):
        cache_key = 'KeywordArticles:' + keyword
        cached_result = redis_cache_client.get(cache_key)
        if cached_result is not None:
            if not cached_result:
                return []
            try:
                article_ids = cached_result.split(',')
                return [int(article_id) for article_id in article_ids]
            except ValueError:
                logging.warning('Key "%s" contains wrong value: %s', cache_key, cached_result)
                redis_cache_client.delete(cache_key)

        pattern = '*%s*:*' % keyword.lower()
        cursor, members = cls.redis_client.sscan(cls.KEY, match=pattern, count=search_limit)
        if members:
            article_ids = [member.rsplit(':', 1)[-1] for member in members[:result_limit]]
            result = [int(article_id) for article_id in article_ids]
        else:
            article_ids = result = []

        redis_cache_client.set(cache_key, ','.join(article_ids), ex=CONFIG.DEFAULT_CACHE_TIME)

        return result
