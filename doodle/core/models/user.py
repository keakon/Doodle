# -*- coding: utf-8 -*-

from hashlib import md5

from doodle.config import CONFIG
from doodle.core.property import BooleanProperty, IntegerProperty, StringProperty

from .base_model import JSONModel, IDModel


class User(IDModel):
    email = StringProperty()
    name = StringProperty()
    site = StringProperty()
    banned = BooleanProperty()

    def _save_relative(self, redis_client, inserting=False):
        if inserting:
            user_email = UserEmail(email=self.email, id=self.id)
            user_email.save(redis_client, inserting=True)

    def _get_relative_keys(self, inserting=False):
        if inserting:
            return [UserEmail.KEY]
        return []

    @classmethod
    def get_by_email(cls, email):
        user_id = UserEmail.get_user_id_by_email(email)
        if user_id:
            return cls.get_by_id(user_id)

    @classmethod
    def get_by_emails(cls, emails):
        user_ids = UserEmail.get_user_ids_by_emails(emails)
        user_ids = [int(user_id) for user_id in user_ids if user_id is not None]
        if user_ids:
            users = cls.get_by_ids(user_ids)
            if users:
                return {user.id: user for user in users}
        return {}

    def get_avatar(self):
        return '/avatar/' + md5(self.email).hexdigest()

    def is_admin(self):
        return self.id == CONFIG.ADMIN_USER_ID


class UserEmail(JSONModel):
    email = StringProperty()
    id = IntegerProperty()

    @classmethod
    def get_user_id_by_email(cls, email):
        user_id = cls.redis_client.hget(cls.KEY, email)
        if user_id:
            return int(user_id)

    @classmethod
    def get_user_ids_by_emails(cls, emails):
        return cls.redis_client.hmget(cls.KEY, emails)

    def _save_self(self, redis_client, inserting=False):
        if self.id:
            redis_client.hset(self.KEY, self.email, self.id)
        else:
            redis_client.hdel(self.KEY, self.email)
