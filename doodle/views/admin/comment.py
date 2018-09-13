# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from doodle.core.models.comment import Comment
from doodle.core.models.fragment_cache import FragmentCache
from doodle.core.redis_client import redis_main_client

from ..base_handler import AdminHandler


class CommentHandler(AdminHandler):
    def delete(self, comment_id):
        comment = Comment.get_by_id(comment_id)
        if not comment:
            raise HTTPError(404)

        if comment.public:
            comment.public = False
            comment.save(relative=False, transactional=False)
            FragmentCache.delete('sidebar')


class UserCommentsHandler(AdminHandler):
    def delete(self, comment_id):
        comment = Comment.get_by_id(comment_id)
        if not comment:
            raise HTTPError(404)

        user_id = comment.user_id
        if not user_id:
            raise HTTPError(404)

        comments_json = Comment.redis_client.lrange(Comment.KEY, 0, -1)
        if comments_json:
            pipe = redis_main_client.pipeline(transaction=False)
            for comment_json in comments_json:
                comment = Comment.from_json(comment_json)
                if comment.user_id == user_id and comment.public:
                    comment.public = False
                    comment.save(pipe, relative=False, transactional=False)
            pipe.execute()
            FragmentCache.delete('sidebar')
