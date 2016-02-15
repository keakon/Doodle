# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from doodle.core.models.article import ArticleHitCount
from doodle.core.models.category import Category, CategoryArticles
from doodle.core.models.comment import ArticleComments

from ..base_handler import ArticlesHandler


class CategoryArticlesHandler(ArticlesHandler):
    def get(self, category_name):
        cursor = self.cursor()

        if not Category.exists(category_name):
            raise HTTPError(404)

        articles, next_cursor = CategoryArticles.get_articles(category_name, cursor)
        if articles:
            article_ids = [article.id for article in articles]
            hit_counts = ArticleHitCount.get_by_ids(article_ids)
            replies_dict = ArticleComments.get_comment_count_of_articles(article_ids)
        else:
            hit_counts = replies_dict = {}
            next_cursor = None

        self.render('web/category_articles.html', {
            'title': u'分类《%s》' % category_name,
            'page': 'category_articles',
            'cursor': cursor,
            'next_cursor': next_cursor,
            'category_name': category_name,
            'articles': articles,
            'hit_counts': hit_counts,
            'replies_dict': replies_dict
        })
