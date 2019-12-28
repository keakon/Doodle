# -*- coding: utf-8 -*-

from doodle.core.models.article import Article, ArticleUpdateTime, PublicArticlePublishTime, PrivateArticlePublishTime
from doodle.core.models.category import CategoryArticle
from doodle.core.models.tag import TagArticle
from doodle.core.redis_client import redis_main_client


redis_main_client.delete(PublicArticlePublishTime.KEY, ArticleUpdateTime.KEY, PrivateArticlePublishTime.KEY)
articles_data = redis_main_client.lrange(Article.KEY, 0, -1)
for article_data in articles_data:
    article = Article.from_json(article_data)
    if article.public:
        PublicArticlePublishTime(article_id=article.id, time=article.pub_time).save(redis_main_client)
        ArticleUpdateTime(article_id=article.id, time=article.mod_time).save(redis_main_client)
        PrivateArticlePublishTime(article_id=article.id, time=None).save(redis_main_client)
    else:
        PublicArticlePublishTime(article_id=article.id, time=None).save(redis_main_client)
        ArticleUpdateTime(article_id=article.id, time=None).save(redis_main_client)
        PrivateArticlePublishTime(article_id=article.id, time=article.pub_time).save(redis_main_client)

    if article.category:
        CategoryArticle(category=article.category, article_id=article.id, time=article.pub_time).save(redis_main_client, inserting=True)

    for tag_name in article.tags:
        TagArticle(tag=tag_name, article_id=article.id, time=article.pub_time).save(redis_main_client, inserting=True)
