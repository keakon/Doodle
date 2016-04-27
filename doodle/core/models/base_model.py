# -*- coding: utf-8 -*-

import logging

try:
    import ujson as json
except ImportError:
    import json

from redis.client import Pipeline

from doodle.common.errors import PropertyError
from doodle.core.property import BooleanProperty, IntegerProperty, PropertiedClass
from doodle.core.redis_client import redis_main_client


class ClassName(object):
    def __get__(self, obj, objtype=None):
        if objtype:
            return objtype.__name__


class SimpleModel(object):
    KEY = ClassName()  # won't work for grandchild class if changed by child class
    redis_client = redis_main_client


class PropertiedModel(SimpleModel):
    __metaclass__ = PropertiedClass

    def __init__(self, **kwargs):
        super(PropertiedModel, self).__init__()
        self._attributes = {}  # stores real values

        for attr_name in self._properties.iterkeys():
            attr_value = kwargs.get(attr_name)
            setattr(self, attr_name, attr_value)

    def to_dict(self):
        return self._attributes.copy()

    def __eq__(self, other):
        if type(self) is type(other) and self._attributes == other._attributes:
            return True
        return False


class JSONModel(PropertiedModel):
    def __init__(self, **kwargs):
        super(JSONModel, self).__init__(**kwargs)
        self._origin_data = {}  # stores origin data from Redis

    def to_json(self, ensure_ascii=False):
        none_empty_attributes = {}
        for key, value in self._attributes.iteritems():
            prop = self._properties.get(key)
            if prop and not prop.is_empty(value):
                if isinstance(property, BooleanProperty):
                    value = 1 if value else 0  # save space
                none_empty_attributes[key] = value
        return json.dumps(none_empty_attributes, ensure_ascii=ensure_ascii)

    @classmethod
    def from_json(cls, json_content):
        if json_content:
            try:
                json_dict = json.loads(json_content)
                if isinstance(json_dict, dict):
                    entity = cls(**json_dict)
                    entity._origin_data = entity.to_dict()
                    return entity
                logging.warning('Decoded JSON data is not a dict: %s', json_content)
            except ValueError:
                logging.warning('Cannot decode the JSON content: %s', json_content, exc_info=True)

    def save(self, redis_client=None, inserting=False, relative=False, transactional=False):
        u"""
        :param redis_client: Redis 连接或 pipeline 对象
        :param inserting: 是否为即将插入的对象
        :param relative: 是否保存相关的对象
        :param transactional: 是否使用事务保存，只用于主对象，相关对象应设为 False
        :return: None
        """

        if inserting:
            self._check_inserting()

        if not redis_client:
            redis_client = self.redis_client

        if transactional:
            watching_keys = self._get_watching_keys(inserting)
            if relative:
                watching_keys.extend(self._get_relative_keys(inserting))

            def insert(pipe):
                try:
                    pipe.watch(*watching_keys)
                    if inserting:
                        self._populate_required_attributes(pipe)
                    pipe.multi()
                    self._save_self(pipe, inserting)
                    if relative:
                        self._save_relative(pipe, inserting)
                    pipe.execute()
                except Exception as e:
                    logging.exception('failed to save')
                    self._fail_on_save(e, pipe, inserting)

            if isinstance(redis_client, Pipeline):
                insert(redis_client)
            else:
                with redis_client.pipeline(True) as pipe:
                    insert(pipe)
        else:
            try:
                if relative:
                    self._populate_required_attributes(redis_client)
                self._save_self(redis_client, inserting)
                if relative:
                    self._save_relative(redis_client, inserting)
            except Exception as e:
                logging.exception('failed to save')
                self._fail_on_save(e, redis_client, inserting)

    def _check_inserting(self):
        pass

    def _get_watching_keys(self, inserting=False):
        return [self.KEY]

    def _get_relative_keys(self, inserting=False):
        return []

    def _populate_required_attributes(self, redis_client):
        pass

    def _save_self(self, redis_client, inserting=False):
        raise NotImplementedError()

    def _save_relative(self, redis_client, inserting=False):
        pass

    def _fail_on_save(self, exception, redis_client, inserting=False):
        raise


class HashModel(JSONModel):
    @classmethod
    def get(cls):
        json_content = cls.redis_client.get(cls.KEY)
        if json_content:
            return cls.from_json(json_content)

    def _save_self(self, pipeline, inserting=False):
        pipeline.set(self.KEY, self.to_json())


class IDModel(JSONModel):
    id = IntegerProperty()

    @classmethod
    def count(cls):
        return cls.redis_client.llen(cls.KEY)

    @classmethod
    def get_by_id(cls, entity_id):
        entity_id = int(entity_id)
        if entity_id <= 0 or isinstance(entity_id, long):
            return
        json_content = cls.redis_client.lindex(cls.KEY, entity_id - 1)
        if json_content:
            return cls.from_json(json_content)

    @classmethod
    def get_by_ids(cls, ids, filter_empty=False):
        if not ids:
            return []

        results = cls._get_data_by_ids(ids)

        if filter_empty:
            entities = [cls.from_json(json_content)
                        for json_content in results
                        if json_content]
            return [entity for entity in entities if entity]
        else:
            return [cls.from_json(json_content)
                    for json_content in results]

    @classmethod
    def _get_data_by_ids(cls, ids):
        key = cls.KEY
        pipe = cls.redis_client.pipeline(transaction=False)
        for entity_id in ids:
            # todo: check id > 0
            pipe.lindex(key, int(entity_id) - 1)
        return pipe.execute()

    def save(self, redis_client=None, inserting=False, relative=True, transactional=True):
        super(IDModel, self).save(redis_client, inserting, relative, transactional)

    def _check_inserting(self):
        if self.id is not None:
            raise PropertyError('cannot insert a %s object with id' % self.__class__.__name__)

    def _populate_required_attributes(self, pipeline):
        self.id = pipeline.llen(self.KEY) + 1

    def _save_self(self, pipeline, inserting=False):
        if inserting:
            pipeline.rpush(self.KEY, self.to_json())
        else:
            if self.id is None:
                raise PropertyError('cannot save a %s object without id' % self.__class__.__name__)
            pipeline.lset(self.KEY, self.id - 1, self.to_json())

    def _fail_on_save(self, exception, pipeline, inserting=False):
        if inserting:
            self.id = None
        raise


class PublicModel(IDModel):
    public = BooleanProperty()

    @classmethod
    def get_by_ids(cls, ids, filter_empty=False, public_only=False):
        if not ids:
            return []

        results = cls._get_data_by_ids(ids)

        if filter_empty or public_only:
            entities = [cls.from_json(json_content)
                        for json_content in results
                        if json_content]
            if public_only:
                return [entity for entity in entities
                        if entity and entity.public]
            return [entity for entity in entities if entity]
        return [cls.from_json(json_content)
                for json_content in results]
