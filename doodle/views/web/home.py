# -*- coding: utf-8 -*-

from doodle.config import CONFIG
from doodle.core.models.article import Article, ArticleHitCount
from doodle.core.models.comment import ArticleComments

from ..base_handler import UserHandler


class HomeHandler(UserHandler):
    def get(self):
        cursor = self.get_cursor()
        if cursor:
            self.set_cache(CONFIG.DEFAULT_CACHE_TIME, is_public=False if self.current_user else None)

        articles, next_cursor = Article.get_articles_for_homepage(cursor)
        if articles:
            article_ids = [article.id for article in articles]
            hit_counts = ArticleHitCount.get_by_ids(article_ids)
            replies_dict = ArticleComments.get_comment_count_of_articles(article_ids)
        else:
            hit_counts = replies_dict = {}

        self.render('web/home.html', {
            'title': CONFIG.BLOG_TITLE,
            'page': 'home',
            'articles': articles,
            'hit_counts': hit_counts,
            'replies_dict': replies_dict,
            'cursor': cursor,
            'next_cursor': next_cursor
        })

    def compute_etag(self):
        if self.get_cursor() and self.is_xhr():
            return super(HomeHandler, self).compute_etag()
