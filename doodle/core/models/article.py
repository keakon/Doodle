# -*- coding: utf-8 -*-

from difflib import get_close_matches

from doodle.core.property import BooleanProperty, DateTimeProperty, IntegerProperty, ListProperty, StringProperty
from doodle.config import CONFIG
from doodle.common.content_format import format_content
from doodle.common.errors import IntegrityError
from doodle.common.url import quoted_string
from doodle.common.time_format import datetime_to_timestamp, parse_date_for_url, LOCAL_TIMEZONE, SECONDS_IN_A_DAY

from .base_model import JSONModel, PublicModel
from .count import Count
from .category import Category, CategoryArticle
from .keyword import KeywordArticle
from .tag import TagArticle


class Article(PublicModel):
    title = StringProperty()
    url = StringProperty()
    content = StringProperty()
    format = IntegerProperty()
    category = StringProperty()
    tags = ListProperty()
    keywords = StringProperty()
    public = BooleanProperty()
    pub_time = DateTimeProperty(auto_now=True)
    mod_time = DateTimeProperty(auto_now=True)

    def quoted_url(self):
        return quoted_string(self.url)

    def category_name(self):
        if self.category:
            return Category.get_parent_path_and_name(self.category)[1]

    def html_summary(self):
        content = self.content
        if CONFIG.SUMMARY_DELIMETER.search(content):
            summary = CONFIG.SUMMARY_DELIMETER.split(content, 1)[0]
        elif CONFIG.SUMMARY_DELIMETER2.search(content):
            summary = CONFIG.SUMMARY_DELIMETER2.split(content, 1)[0]
        else:
            summary = content
        return format_content(summary, self.format)

    def html_content(self):
        content = self.content
        if CONFIG.SUMMARY_DELIMETER.search(content):
            content = CONFIG.SUMMARY_DELIMETER.sub('', content, 1)
        elif CONFIG.SUMMARY_DELIMETER2.search(content):
            content = CONFIG.SUMMARY_DELIMETER2.split(content, 1)[1]
        return format_content(content, self.format)

    def _get_relative_keys(self, inserting=False):
        relative_keys = [PublicArticlePublishTime.KEY, ArticleUpdateTime.KEY, PrivateArticlePublishTime.KEY]
        if inserting:
            relative_keys.append(ArticleURL.KEY)
            if self.category:
                relative_keys.extend([Category.KEY, CategoryArticle.KEY % self.category])
            if self.tags:
                relative_keys.extend([TagArticle.KEY % tag for tag in self.tags])
            if self.keywords:
                relative_keys.append(KeywordArticle.KEY)
        else:
            origin_data = self._origin_data

            old_url = origin_data.get('url')
            if old_url and old_url != self.url:
                relative_keys.append(ArticleURL.KEY)

            old_category = origin_data.get('category') or ''
            if old_category != self.category:
                relative_keys.append(Category.KEY)
                if old_category:
                    relative_keys.append(CategoryArticle.KEY % old_category)
                if self.category:
                    relative_keys.append(CategoryArticle.KEY % self.category)

            old_tags = origin_data.get('tags') or []
            if old_tags != self.tags:
                relative_keys.extend([TagArticle.KEY % tag for tag in set(self.tags + old_tags)])

            old_keywords = origin_data.get('keywords')
            if old_keywords != self.keywords:
                relative_keys.append(KeywordArticle.KEY)
        return relative_keys

    def _save_relative(self, redis_client, inserting=False):
        if inserting:
            ArticleURL(url=self.url, article_id=self.id).save(redis_client, inserting=True)
            if self.category:
                CategoryArticle(category=self.category, article_id=self.id, time=self.pub_time).save(redis_client, inserting=True)
            if self.tags:
                for tag_name in self.tags:
                    TagArticle(tag=tag_name, article_id=self.id, time=self.pub_time).save(redis_client, inserting=True)
            if self.keywords:
                KeywordArticle(keywords=self.keywords, article_id=self.id).save(redis_client, inserting=True)
        else:
            origin_data = self._origin_data

            old_url = origin_data.get('url')
            if old_url and old_url != self.url:
                ArticleURL(url=self.url, article_id=self.id).save(redis_client, inserting=True)
                ArticleURL(url=old_url, article_id=None).save(redis_client)

            old_category = origin_data.get('category')
            if old_category != self.category:
                if self.category:
                    CategoryArticle(category=self.category, article_id=self.id, time=self.pub_time).save(redis_client, inserting=True)
                if old_category:
                    CategoryArticle(category=old_category, article_id=self.id, time=None).save(redis_client)

            old_tags = origin_data.get('tags')
            if old_tags != self.tags:
                old_tag_set = set(old_tags)
                tag_set = set(self.tags)
                added_tag_set = tag_set - old_tag_set
                removed_tag_set = old_tag_set - tag_set
                for tag_name in added_tag_set:
                    TagArticle(tag=tag_name, article_id=self.id, time=self.pub_time).save(redis_client, inserting=True)
                for tag_name in removed_tag_set:
                    TagArticle(tag=tag_name, article_id=self.id, time=None).save(redis_client)

            old_keywords = origin_data.get('keywords')
            if old_keywords != self.keywords:
                if self.keywords:
                    KeywordArticle(keywords=self.keywords, article_id=self.id).save(redis_client, inserting=True)
                if old_keywords:
                    KeywordArticle(keywords=old_keywords, article_id=self.id).delete(redis_client)

        if self.public:
            PublicArticlePublishTime(article_id=self.id, time=self.pub_time).save(redis_client)
            ArticleUpdateTime(article_id=self.id, time=self.mod_time).save(redis_client)
            PrivateArticlePublishTime(article_id=self.id, time=None).save(redis_client)
        else:
            PublicArticlePublishTime(article_id=self.id, time=None).save(redis_client)
            ArticleUpdateTime(article_id=self.id, time=None).save(redis_client)
            PrivateArticlePublishTime(article_id=self.id, time=self.pub_time).save(redis_client)

    @classmethod
    def exist_url(cls, url):
        return ArticleURL.get_article_id_by_url(url) is not None

    @classmethod
    def get_by_url(cls, url):
        article_id = ArticleURL.get_article_id_by_url(url)
        if article_id:
            return cls.get_by_id(article_id)

    @classmethod
    def search(cls, date, url):
        article_ids = PublicArticlePublishTime.get_article_ids_by_data(date)
        if article_ids:
            articles = Article.get_by_ids(article_ids, public_only=True)
            if articles:
                if len(articles) == 1:
                    return articles[0].quoted_url()
                urls = [article.quoted_url() for article in articles]
                matched_urls = get_close_matches(url, urls, 1, 0)
                return matched_urls[0]

    @classmethod
    def get_articles_and_next_cursor(cls, article_ids_with_time, public_only=True, limit=CONFIG.ARTICLES_PER_PAGE):
        article_ids = [int(article_id) for article_id, timestamp in article_ids_with_time]
        if len(article_ids) == limit:
            next_cursor = article_ids_with_time[-1][1]
        else:
            next_cursor = None
        articles = Article.get_by_ids(article_ids, filter_empty=True, public_only=public_only)
        return articles, next_cursor

    @classmethod
    def get_articles_for_homepage(cls, cursor=None, limit=CONFIG.ARTICLES_PER_PAGE):
        article_ids_with_time = PublicArticlePublishTime.get_article_ids(cursor, limit=limit)
        if article_ids_with_time:
            return cls.get_articles_and_next_cursor(article_ids_with_time, limit=limit)
        return [], None

    @staticmethod
    def get_unpublished_articles(cls, page, page_size=CONFIG.ARTICLES_PER_PAGE):
        article_ids = PrivateArticlePublishTime.get_article_ids_for_page(page, page_size)
        if article_ids:
            return cls.get_by_ids(article_ids, filter_empty=True)
        return []

    @classmethod
    def get_articles_count(cls, public=True):
        time_class = PublicArticlePublishTime if public else PrivateArticlePublishTime
        return time_class.get_count()

    @classmethod
    def get_articles_for_feed(cls, limit=CONFIG.ARTICLES_FOR_FEED):
        if CONFIG.SORT_FEED_BY_UPDATE_TIME:
            article_ids = ArticleUpdateTime.get_article_ids_for_page(1, limit)
        else:
            article_ids = PublicArticlePublishTime.get_article_ids(None, with_time=False, limit=limit)
        if article_ids:
            return cls.get_by_ids(article_ids, public_only=True)
        return []

    def get_previous_article(self):
        time_class = PublicArticlePublishTime if self.public else PrivateArticlePublishTime
        article_id = time_class.get_previous_article_id(self.pub_time)
        if article_id:
            return Article.get_by_id(article_id)

    def get_next_article(self):
        time_class = PublicArticlePublishTime if self.public else PrivateArticlePublishTime
        article_id = time_class.get_next_article_id(self.pub_time)
        if article_id:
            return Article.get_by_id(article_id)

    def get_nearby_articles(self):
        time_class = PublicArticlePublishTime if self.public else PrivateArticlePublishTime
        previous_article_id = time_class.get_previous_article_id(self.pub_time)
        next_article_id = time_class.get_next_article_id(self.pub_time)
        if previous_article_id:
            if next_article_id:
                return Article.get_by_ids((previous_article_id, next_article_id))
            else:
                return Article.get_by_id(previous_article_id), None
        else:
            if next_article_id:
                return None, Article.get_by_id(next_article_id)
            else:
                return None, None


class ArticleURL(JSONModel):
    url = StringProperty()
    article_id = IntegerProperty()

    @classmethod
    def get_article_id_by_url(cls, url):
        article_id = cls.redis_client.hget(cls.KEY, url)
        if article_id:
            return int(article_id)

    @classmethod
    def get_by_url(cls, url):
        article_id = cls.get_article_id_by_url(url)
        if article_id:
            return cls(url=url, id=article_id)

    @classmethod
    def search_by_date(cls, date, limit=CONFIG.SEARCH_PAGE_SIZE):
        cursor, result = cls.redis_client.hscan(cls.KEY, 0, date + '*', limit)
        return result

    def _save_self(self, redis_client, inserting=False):
        if self.url:
            if self.article_id:
                redis_client.hset(self.KEY, self.url, self.article_id)
            else:
                redis_client.hdel(self.KEY, self.url)

    def _check_inserting(self):
        article_id = self.get_article_id_by_url(self.url)
        if article_id:
            article_id = int(article_id)
            if article_id != self.article_id:
                raise IntegrityError('article url "%s" has been used by article %d' % (self.url, article_id))


class ArticleHitCount(Count):
    pass


class ArticleTime(JSONModel):
    article_id = IntegerProperty()
    time = IntegerProperty()

    @classmethod
    def get_article_ids_for_page(cls, page, page_size=CONFIG.ARTICLES_PER_PAGE):
        if page_size <= 0:
            return cls.redis_client.zrevrangebyscore(cls.KEY, '+inf', 0)
        if page < 1:
            page = 1
        start_index = (page - 1) * page_size
        return cls.redis_client.zrevrangebyscore(cls.KEY, '+inf', 0, start_index, page_size)

    @classmethod
    def get_article_ids(cls, cursor=None, with_time=True, limit=CONFIG.ARTICLES_PER_PAGE):
        if cursor is None:
            return cls.redis_client.zrevrange(cls.KEY, 0, limit - 1, withscores=with_time, score_cast_func=int)
        else:
            return cls.redis_client.zrevrangebyscore(cls.KEY, '(%d' % cursor, 0, 0, limit, withscores=with_time, score_cast_func=int)

    @classmethod
    def get_previous_article_id(cls, publish_time):
        result = cls.redis_client.zrevrangebyscore(cls.KEY, '(%d' % publish_time, 0, 0, 1)
        if result:
            return int(result[0])

    @classmethod
    def get_next_article_id(cls, publish_time):
        result = cls.redis_client.zrangebyscore(cls.KEY, '(%d' % publish_time, '+inf', 0, 1)
        if result:
            return int(result[0])

    @classmethod
    def get_article_ids_by_data(cls, date):
        from_dt = parse_date_for_url(date)
        if from_dt:
            from_dt = from_dt.replace(tzinfo=LOCAL_TIMEZONE)
            from_time = datetime_to_timestamp(from_dt)
            to_time = from_time + SECONDS_IN_A_DAY
            from_time -= SECONDS_IN_A_DAY
            article_ids = cls.redis_client.zrangebyscore(cls.KEY, from_time, to_time)
            return [int(article_id) for article_id in article_ids]
        return []

    @classmethod
    def get_count(cls):
        return cls.redis_client.zcard(cls.KEY) or 0

    def _save_self(self, redis_client, inserting=False):
        if self.article_id:
            if self.time:
                redis_client.zadd(self.KEY, self.time, self.article_id)
            else:
                redis_client.zrem(self.KEY, self.article_id)


class PublicArticlePublishTime(ArticleTime):
    pass


class PrivateArticlePublishTime(ArticleTime):
    pass


class ArticleUpdateTime(ArticleTime):
    pass
