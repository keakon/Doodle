# -*- coding: utf-8 -*-

import re

from doodle.config import CONFIG
from doodle.core.property import IntegerProperty, StringProperty
from doodle.common.errors import IntegrityError

from .base_model import JSONModel, SimpleModel


class Category(SimpleModel):
    @classmethod
    def get_all(cls):
        return cls.redis_client.hgetall(cls.KEY)

    @classmethod
    def get_all_paths(cls):
        category_paths = []
        categories = Category.get_all()
        if categories:
            for category_name, category_parent_path in categories.iteritems():
                if category_parent_path:
                    category_paths.append(u'%s:%s' % (category_parent_path, category_name))
                else:
                    category_paths.append(category_name)
            category_paths.sort()
        return category_paths

    @classmethod
    def get_all_names_with_paths(cls):
        category_list = []
        categories = Category.get_all()
        if categories:
            for category_name, category_parent_path in categories.iteritems():
                category_name = unicode(category_name, 'utf-8')
                if category_parent_path:
                    category_parent_path = unicode(category_parent_path, 'utf-8')
                    category_list.append((category_name, u'%s:%s' % (category_parent_path, category_name)))
                else:
                    category_list.append((category_name, category_name))
            category_list.sort(key=lambda category: category[1])
        return category_list

    @classmethod
    def get_sub_category_names(cls, name):
        category_names = []
        categories = Category.get_all()
        if categories:
            pattern = re.compile(r'^(.+:)?%s(:.+)?$' % re.escape(name))
            for category_name, category_parent_path in categories.iteritems():
                if category_parent_path and pattern.match(unicode(category_parent_path, 'utf-8')):
                    category_names.append(category_name)
        return category_names

    @classmethod
    def exists(cls, name):
        return cls.redis_client.hexists(cls.KEY, name)

    @classmethod
    def get_parent_path(cls, name):
        return cls.redis_client.hget(cls.KEY, name)

    @classmethod
    def get_parent_path_and_name(cls, path):
        parts = path.rsplit(':', 1)
        if len(parts) == 1:
            return '', path
        else:
            return parts

    @classmethod
    def add(cls, path):
        parent_path, name = cls.get_parent_path_and_name(path)

        with cls.redis_client.pipeline(True) as pipe:
            pipe.watch(cls.KEY)
            existing_path = pipe.hget(cls.KEY, name)
            if existing_path is not None:
                if existing_path != parent_path:
                    raise IntegrityError('category %s already exists' % name, category_name=name, category_parent_path=existing_path)
                else:
                    return
            pipe.multi()
            pipe.hset(cls.KEY, name, parent_path)
            pipe.execute()


class CategoryArticle(JSONModel):
    KEY = 'CategoryArticle:%s'

    category = StringProperty()
    article_id = IntegerProperty()
    time = IntegerProperty()

    def _get_watching_keys(self, inserting=False):
        return [self.KEY % self.category]

    def _save_self(self, redis_client, inserting=False):
        key = self.KEY % self.category
        if self.time:
            redis_client.zadd(key, {self.article_id: self.time})
        else:
            redis_client.zrem(key, self.article_id)


class CategoryArticles(JSONModel):  # 聚合子类的文章并缓存
    KEY = 'CategoryArticles:%s'

    @classmethod
    def get_article_ids(cls, category_name, cursor=None, limit=CONFIG.ARTICLES_PER_PAGE):
        redis_client = cls.redis_client
        key = cls.KEY % category_name
        if not redis_client.exists(key):
            sub_category_names = Category.get_sub_category_names(category_name)
            category_names = [category_name] + sub_category_names
            keys = [CategoryArticle.KEY % name for name in category_names]
            redis_client.zunionstore(key, keys, aggregate='MAX')  # 不能跨库执行这个操作，所以不能使用 redis_cache_client
            redis_client.expire(key, CONFIG.CATEGORY_ARTICLES_CACHE_TIME)

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
