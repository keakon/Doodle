# -*- coding: utf-8 -*-

import re

from doodle.common.content_format import format_content
from doodle.core.property import *
from doodle.config import CONFIG

from .article import Article
from .base_model import JSONModel, PublicModel
from .user import User


class Comment(PublicModel):
    article_id = IntegerProperty()
    user_id = IntegerProperty()
    content = StringProperty()
    format = IntegerProperty()
    ua = ListProperty()
    time = DateTimeProperty(auto_now=True)

    HTML_PATTERN = re.compile('<.*?>|\&.*?\;', re.UNICODE)
    ROOT_LINK_PATTERN = re.compile(r'<a href="/([^"]*)">')
    ANCHOR_LINK_PATTERN = re.compile(r'<a href="#([^"]*)">')
    REPLY_LINK_PATTERN = re.compile(r'<a href="[^"]*#comment-id-(\d+)">')

    def html_content(self):
        return format_content(self.content, self.format)

    def html_content_with_full_url(self, article_url): # for email and ATOM
        content = self.html_content()
        content = self.ROOT_LINK_PATTERN.sub(r'<a href="%s/\1">' % CONFIG.MAJOR_HOST_URL, content)
        content = self.ANCHOR_LINK_PATTERN.sub(r'<a href="%s#\1">' % article_url, content)
        return content

    def striped_html_content(self, length=CONFIG.LATEST_COMMENTS_LENGTH):
        result = self.HTML_PATTERN.sub(' ', self.html_content())
        return result[:length].strip()

    @classmethod
    def get_comments_of_article(cls, article_id, order, page, page_size=CONFIG.COMMENTS_PER_PAGE, public_only=True):
        comment_ids = ArticleComments.get_by_article_id(article_id, order, page, page_size)
        if comment_ids:
            has_next_page = len(comment_ids) == page_size
            return Comment.get_by_ids(comment_ids, filter_empty=True, public_only=public_only), has_next_page
        return [], False

    @classmethod
    def get_latest_comments(cls, limit=CONFIG.LATEST_COMMENTS_FOR_SIDEBAR):
        comments_json = cls.redis_client.lrange(cls.KEY, -limit, -1)
        if comments_json:
            comments = []
            for comment_json in reversed(comments_json):
                comment = Comment.from_json(comment_json)
                if comment.public:
                    comments.append(comment)
            if comments:
                article_ids = set()
                user_ids = set()
                for comment in comments:
                    article_ids.add(comment.article_id)
                    user_ids.add(comment.user_id)
                articles = Article.get_by_ids(article_ids, public_only=True)
                if articles:
                    article_dict = {article.id: article for article in articles}
                    users = User.get_by_ids(user_ids, filter_empty=True)
                    if users:
                        user_dict = {user.id: user for user in users}
                        return comments, article_dict, user_dict
        return [], {}, {}

    def _get_relative_keys(self, inserting=False):
        if inserting:
            return [ArticleComments.KEY % self.article_id]
        return []

    def _save_relative(self, redis_client, inserting=False):
        if inserting:
            ArticleComments.append_comment_to_article(redis_client, self.id, self.article_id)


class ArticleComments(JSONModel):
    KEY = 'ArticleComments:%d'

    article_id = IntegerProperty()
    comment_ids = ListProperty(int)

    def _get_watching_keys(self, inserting=False):
        return [self.KEY % self.article_id]

    def _save_self(self, redis_client, inserting=False):
        key = self.KEY % self.article_id
        redis_client.delete(key)
        for comment_id in self.comment_ids:
            redis_client.rpush(key, comment_id)

    @classmethod
    def get_by_article_id(cls, article_id, order, page, page_size=CONFIG.COMMENTS_PER_PAGE):
        key = cls.KEY % article_id
        if page < 1:
            page = 1
        if order:
            start_index = (page - 1) * page_size
            end_index = start_index + page_size -1
        else:
            end_index = -(page - 1) * page_size - 1
            start_index = end_index - page_size + 1
        comment_ids = cls.redis_client.lrange(key, start_index, end_index)
        if comment_ids and not order:
            comment_ids.reverse()
        return comment_ids

    @classmethod
    def append_comment_to_article(cls, redis_client, comment_id, article_id):
        redis_client.rpush(cls.KEY % article_id, comment_id)

    @classmethod
    def get_comment_count_of_article(cls, article_id):
        return cls.redis_client.llen(cls.KEY % article_id)

    @classmethod
    def get_comment_count_of_articles(cls, article_ids):
        with cls.redis_client.pipeline(transaction=False) as pipe:
            for article_id in article_ids:
                pipe.llen(cls.KEY % article_id)
            counts = pipe.execute()

        count_zip = zip(article_ids, [int(count) for count in counts])
        return dict(count_zip)
