# -*- coding: utf-8 -*-

from itertools import izip

from doodle.config import CONFIG
from doodle.core.property import IntegerProperty, StringProperty

from .base_model import JSONModel, SimpleModel


class Tag(SimpleModel):
    @classmethod
    def get_all(cls):
        names = cls.redis_client.smembers(cls.KEY)
        return [unicode(name, 'utf-8') for name in names]

    @classmethod
    def add(cls, name):
        cls.redis_client.sadd(cls.KEY, name)

    @classmethod
    def exists(cls, name):
        return cls.redis_client.sismember(cls.KEY, name)

    @classmethod
    def get_count(cls, name):
        return cls.redis_client.zcard(TagArticle.KEY % name)

    @classmethod
    def get_counts(cls):
        names = cls.get_all()
        if names:
            with cls.redis_client.pipeline(transaction=False) as pipe:
                for name in names:
                    pipe.zcard(TagArticle.KEY % name)
                counts = pipe.execute()
            return dict(izip(names, counts))
        return {}


class TagArticle(JSONModel):
    KEY = 'TagArticle:%s'

    tag = StringProperty()
    article_id = IntegerProperty()
    time = IntegerProperty()

    def _get_watching_keys(self, inserting=False):
        return [self.KEY % self.tag]

    def _save_self(self, redis_client, inserting=False):
        key = self.KEY % self.tag
        if self.time:
            redis_client.zadd(key, {self.article_id: self.time})
        else:
            redis_client.zrem(key, self.article_id)

    @classmethod
    def get_article_ids(cls, tag_name, cursor=None, limit=CONFIG.ARTICLES_PER_PAGE):
        redis_client = cls.redis_client
        key = cls.KEY % tag_name
        if cursor is None:
            return redis_client.zrevrange(key, 0, limit - 1, withscores=True, score_cast_func=int)
        else:
            return redis_client.zrevrangebyscore(key, '(%d' % cursor, 0, 0, limit, withscores=True, score_cast_func=int)

    @classmethod
    def get_articles(cls, category_name, cursor=None, limit=CONFIG.ARTICLES_PER_PAGE):
        article_ids_with_time = cls.get_article_ids(category_name, cursor)
        if article_ids_with_time:
            from .article import Article
            return Article.get_articles_and_next_cursor(article_ids_with_time, limit=limit)
        return [], None
