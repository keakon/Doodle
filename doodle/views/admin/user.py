# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from doodle.core.models.comment import Comment
from doodle.core.models.user import User

from ..base_handler import AdminHandler


class BanUserHandler(AdminHandler):
    def post(self, comment_id):
        comment = Comment.get_by_id(comment_id)
        if not comment and comment.user_id:
            raise HTTPError(404)

        user = User.get_by_id(comment.user_id)
        if not user:
            raise HTTPError(404)

        if not user.banned:
            user.banned = True
            user.save(relative=False, transactional=False)
