# -*- coding: utf-8 -*-

import time
from unittest import TestCase

from doodle.common.errors import PropertyError
from doodle.core.models.article import Article, ArticleURL, ArticleTime, ArticleUpdateTime


class ArticleTestCase(TestCase):
    def setUp(self):
        super(ArticleTestCase, self).setUp()
        Article.redis_client.flushdb()

    def test_save_and_get_by_id(self):
        self.assertIsNone(Article.get_by_id(1))

        now = int(time.time())
        article = Article(
            title='test title',
            url='test-url',
            content=u'测试',
            category='test',
            tags=('test1', 'test2'),
        )
        self.assertRaises(PropertyError, article.save)
        article.save(inserting=True)
        self.assertEqual(article.id, 1)

        saved_article = Article.get_by_id(1)
        self.assertEqual(article, saved_article)
        self.assertGreaterEqual(saved_article.pub_time, now)
        self.assertGreaterEqual(saved_article.mod_time, now)
        self.assertIsNone(Article.get_by_id(2))

        saved_article.title = u'测试'
        saved_article.save()
        saved_article = Article.get_by_id(1)
        self.assertEqual(saved_article.title, u'测试')
        self.assertIsNone(Article.get_by_id(2))
        self.assertRaises(PropertyError, saved_article.save, inserting=True)

        article2 = Article(
            title='test',
            category='test',
            tags=('test1', 'test2'),
            pub_time=1,
            mod_time=2
        )
        article2.save(inserting=True)
        self.assertEqual(article2.id, 2)
        saved_article2 = Article.get_by_id(2)
        self.assertEqual(article2, saved_article2)
