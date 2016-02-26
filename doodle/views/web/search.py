# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from doodle.config import CONFIG
from doodle.core.models.article import Article, ArticleHitCount
from doodle.core.models.keyword import KeywordArticle
from doodle.core.models.comment import ArticleComments

from ..base_handler import BaseHandler


class SearchHandler(BaseHandler):
    def get(self):
        keywords = self.get_argument('keywords', None)
        if keywords:
            article_ids = KeywordArticle.query_by_keyword(keywords)
            if article_ids:
                articles = Article.get_by_ids(article_ids, public_only=True)
                article_ids = [article.id for article in articles]
                hit_counts = ArticleHitCount.get_by_ids(article_ids)
                replies_dict = ArticleComments.get_comment_count_of_articles(article_ids)
            else:
                articles = []
                hit_counts = replies_dict = {}

            self.set_cache(CONFIG.DEFAULT_CACHE_TIME, is_public=True)
            self.render('web/search.html', {
                'title': u'搜索《%s》' % keywords,
                'page': 'search',
                'keywords': keywords,
                'articles': articles,
                'hit_counts': hit_counts,
                'replies_dict': replies_dict
            })
        else:
            raise HTTPError(400)
