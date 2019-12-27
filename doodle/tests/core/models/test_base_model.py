# -*- coding: utf-8 -*-

from unittest import TestCase

import json

from doodle.common.errors import PropertyError
from doodle.core.models.base_model import HashModel, IDModel, JSONModel, PropertiedModel, PublicModel, SimpleModel
from doodle.core.property import BooleanProperty, IntegerProperty, ListProperty, Property, StringProperty


class SimpleSubModel(SimpleModel):
    pass


class SimpleSubModel2(SimpleSubModel):
    pass


class SimpleModelTestCase(TestCase):
    def test_key(self):
        self.assertEqual(SimpleModel.KEY, 'SimpleModel')
        self.assertEqual(SimpleSubModel.KEY, 'SimpleSubModel')
        self.assertEqual(SimpleSubModel2.KEY, 'SimpleSubModel2')


class PropertiedTestModel(PropertiedModel):
    a = IntegerProperty()


class PropertiedTestModel2(PropertiedModel):
    a = IntegerProperty()


class PropertiedModelTestCase(TestCase):
    def test_init(self):
        entity = PropertiedTestModel()
        self.assertDictEqual(entity._attributes, {'a': None})

        entity = PropertiedTestModel(a=1)
        self.assertDictEqual(entity._attributes, {'a': 1})

        entity = PropertiedTestModel(b=1)
        self.assertDictEqual(entity._attributes, {'a': None})

        entity = PropertiedTestModel(a=1, b=2)
        self.assertDictEqual(entity._attributes, {'a': 1})

    def test_to_dict(self):
        entity = PropertiedTestModel()
        self.assertDictEqual(entity.to_dict(), {'a': None})

        entity.a = 1
        self.assertDictEqual(entity.to_dict(), {'a': 1})

    def test_eq(self):
        entity = PropertiedTestModel()
        entity2 = PropertiedTestModel()
        self.assertEqual(entity, entity2)

        entity2.a = 1
        self.assertNotEqual(entity, entity2)

        entity3 = PropertiedTestModel2()
        self.assertNotEqual(entity, entity3)

        entity.a = 1
        self.assertEqual(entity, entity2)


class JSONTestModel(JSONModel):
    a = IntegerProperty()
    b = StringProperty()
    c = BooleanProperty()
    d = ListProperty()
    e = Property()

    def _save_self(self, redis_client, inserting=False):
        redis_client.hset(self.KEY, 'self', '1')

    def _save_relative(self, redis_client, inserting=False):
        redis_client.hset(self.KEY, 'relative', '1')


class JSONModelTestCase(TestCase):
    def test_to_dict(self):
        entity = JSONTestModel()
        self.assertDictEqual(entity.to_dict(), {'a': None, 'b': '', 'c': None, 'd': [], 'e': None})

        entity.a = 1
        entity.c = False
        self.assertDictEqual(entity.to_dict(), {'a': 1, 'b': '', 'c': False, 'd': [], 'e': None})

    def test_to_json(self):
        entity = JSONTestModel()
        self.assertEqual(entity.to_json(), '{}')

        entity.a = 1
        entity.c = False
        entity.e = True
        json_content = entity.to_json()
        self.assertDictEqual(json.loads(json_content), {'a': 1, 'c': 0, 'e': True})

        entity.c = None
        json_content = entity.to_json()
        self.assertDictEqual(json.loads(json_content), {'a': 1, 'e': True})

    def test_from_json(self):
        self.assertIsNone(JSONTestModel.from_json(None))
        self.assertIsNone(JSONTestModel.from_json(''))
        self.assertIsNone(JSONTestModel.from_json('1'))

        entity = JSONTestModel.from_json('{}')
        self.assertDictEqual(entity.to_dict(), {'a': None, 'b': '', 'c': None, 'd': [], 'e': None})

        data = {'a': 1, 'c': 0, 'e': True, 'f': 2}
        json_content = json.dumps(data)
        entity = JSONTestModel.from_json(json_content)
        self.assertDictEqual(entity.to_dict(), {'a': 1, 'b': '', 'c': False, 'd': [], 'e': True})

    def test_save(self):
        redis_client = JSONTestModel.redis_client
        key = JSONTestModel.KEY
        redis_client.delete(key)

        entity = JSONTestModel()
        entity.save(relative=False, transactional=False)
        self.assertEqual(redis_client.hget(key, 'self'), '1')
        self.assertIsNone(redis_client.hget(key, 'relative'))

        redis_client.delete(key)
        entity.save(relative=True, transactional=False)
        self.assertEqual(redis_client.hget(key, 'self'), '1')
        self.assertEqual(redis_client.hget(key, 'relative'), '1')

        redis_client.delete(key)
        entity.save(relative=True, transactional=True)
        self.assertEqual(redis_client.hget(key, 'self'), '1')
        self.assertEqual(redis_client.hget(key, 'relative'), '1')


class HashTestModel(HashModel):
    a = IntegerProperty()
    b = StringProperty()
    c = BooleanProperty()
    d = ListProperty()


class HashModelTestCase(TestCase):
    def test_save_and_get(self):
        entity = HashTestModel()
        entity.save()
        self.assertEqual(entity, HashTestModel.get())

        entity.a = 1
        entity.b = '2'
        entity.c = False
        entity.d = [1, 2]
        entity.save()
        self.assertEqual(entity, HashTestModel.get())


class IDTestModel(IDModel):
    a = IntegerProperty()
    b = StringProperty()
    c = BooleanProperty()
    d = ListProperty()


class IDModelTestCase(TestCase):
    def setUp(self):
        super(IDModelTestCase, self).setUp()
        IDTestModel.redis_client.delete(IDTestModel.KEY)

    def test_save_and_get_by_id(self):
        self.assertIsNone(IDTestModel.get_by_id(1))

        entity = IDTestModel()
        entity.save(inserting=True)
        self.assertEqual(entity, IDTestModel.get_by_id(1))

        entity.a = 1
        entity.b = '2'
        entity.c = False
        entity.d = [1, 2]
        entity.save()
        self.assertEqual(entity, IDTestModel.get_by_id(1))

        entity2 = IDTestModel()
        entity2.a = 2
        entity2.save(inserting=True)
        self.assertEqual(entity2, IDTestModel.get_by_id(2))
        self.assertEqual(entity, IDTestModel.get_by_id(1))

        entity = IDTestModel()
        self.assertRaises(PropertyError, entity.save)
        entity.id = 10
        self.assertRaises(PropertyError, entity.save, inserting=True)

    def test_get_by_ids(self):
        self.assertListEqual(IDTestModel.get_by_ids([1, 2]), [None, None])
        self.assertListEqual(IDTestModel.get_by_ids([1, 2], filter_empty=True), [])

        entity = IDTestModel()
        entity.a = 1
        entity.save(inserting=True)
        self.assertListEqual(IDTestModel.get_by_ids([1, 2]), [entity, None])
        self.assertListEqual(IDTestModel.get_by_ids([1, 2], filter_empty=True), [entity])

        entity2 = IDTestModel()
        entity2.a = 2
        entity2.save(inserting=True)
        self.assertListEqual(IDTestModel.get_by_ids([1, 2], filter_empty=True), [entity, entity2])

    def test_count(self):
        self.assertEqual(IDTestModel.count(), 0)
        self.assertEqual(IDTestModel.count(), 0)

        IDTestModel().save(inserting=True)
        self.assertEqual(IDTestModel.count(), 1)

        IDTestModel().save(inserting=True)
        self.assertEqual(IDTestModel.count(), 2)


class PublicTestModel(PublicModel):
    a = IntegerProperty()


class PublicModelTestCase(TestCase):
    def test_get_by_ids(self):
        PublicTestModel.redis_client.delete(PublicTestModel.KEY)

        self.assertListEqual(PublicTestModel.get_by_ids([1, 2]), [None, None])
        self.assertListEqual(PublicTestModel.get_by_ids([1, 2], filter_empty=True), [])
        self.assertListEqual(PublicTestModel.get_by_ids([1, 2], filter_empty=False, public_only=True), [])
        self.assertListEqual(PublicTestModel.get_by_ids([1, 2], filter_empty=True, public_only=True), [])

        entity = PublicTestModel(
            public=False,
            a=1
        )
        entity.save(inserting=True)
        self.assertListEqual(PublicTestModel.get_by_ids([1, 2], public_only=True), [])

        entity2 = PublicTestModel(
            public=True,
            a=2
        )
        entity2.save(inserting=True)
        self.assertListEqual(PublicTestModel.get_by_ids([1, 2], public_only=True), [entity2])

        entity3 = PublicTestModel(
            public=True,
            a=3
        )
        entity3.save(inserting=True)
        self.assertListEqual(PublicTestModel.get_by_ids([1, 2, 3], public_only=True), [entity2, entity3])
