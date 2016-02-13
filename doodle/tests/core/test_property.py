# -*- coding: utf-8 -*-

import calendar
from datetime import datetime
import unittest

from doodle.core.models.base_model import PropertiedModel
from doodle.core.property import BooleanProperty, DateTimeProperty, FloatProperty, IntegerProperty, ListProperty, Property, StringProperty


class Model1(PropertiedModel):
    pass


class Model2(PropertiedModel):
    KEY = 'm2'

    a = Property()


class Model3(Model2):
    b = Property()


class Model4(Model1):
    a = StringProperty()
    b = IntegerProperty()
    c = BooleanProperty()
    d = FloatProperty()
    e = DateTimeProperty()
    f = DateTimeProperty(auto_now=True)


class Model5(Model1):
    a = ListProperty()


class PropertiedClassTestCase(unittest.TestCase):
    def test_properties(self):
        self.assertDictEqual(Model1._properties, {})
        entity = Model1()
        self.assertDictEqual(entity._properties, {})
        entity.a = 1
        self.assertDictEqual(entity._properties, {})

        self.assertListEqual(Model2._properties.keys(), ['a'])
        self.assertIsInstance(Model2._properties.values()[0], Property)

        self.assertItemsEqual(Model3._properties.keys(), ['a', 'b'])

    def test_key(self):
        self.assertEqual(Model1.KEY, 'Model1')
        self.assertEqual(Model2.KEY, 'm2')
        self.assertEqual(Model3.KEY, 'Model3')


class PropertyTestCase(unittest.TestCase):
    def test_init(self):
        entity = Model3()
        self.assertDictEqual(entity._attributes, {'a': None, 'b': None})

        entity = Model3(a=1, b=2)
        self.assertDictEqual(entity._attributes, {'a': 1, 'b': 2})

        entity = Model3(a=1)
        self.assertDictEqual(entity._attributes, {'a': 1, 'b': None})

        entity = Model3(b=1, c=2)
        self.assertDictEqual(entity._attributes, {'a': None, 'b': 1})

    def test_set(self):
        entity = Model3()
        self.assertDictEqual(entity._attributes, {'a': None, 'b': None})
        entity.a = 2
        self.assertDictEqual(entity._attributes, {'a': 2, 'b': None})
        entity.b = '3'
        self.assertDictEqual(entity._attributes, {'a': 2, 'b': '3'})
        entity.c = 4
        self.assertDictEqual(entity._attributes, {'a': 2, 'b': '3'})

    def test_get(self):
        entity = Model2()
        self.assertIsNone(entity.a)
        entity.a = 1
        self.assertEqual(entity.a, 1)

        entity = Model3(a=2)
        self.assertEqual(entity.a, 2)
        entity.b = [1, 3, 2]
        self.assertListEqual(entity.b, [1, 3, 2])
        del entity.b[1]
        self.assertListEqual(entity.b, [1, 2])
        entity.b = entity.b[0]
        self.assertEqual(entity.b, 1)


class StringPropertyTestCase(unittest.TestCase):
    def test_convert(self):
        entity = Model4()
        self.assertEqual(entity.a, '')
        entity.a = '1'
        self.assertEqual(entity.a, '1')
        entity.a = 2
        self.assertEqual(entity.a, '2')
        entity.a = True
        self.assertEqual(entity.a, 'True')
        entity.a = u'哈哈'
        self.assertEqual(entity.a, u'哈哈')
        entity.a = None
        self.assertEqual(entity.a, '')


class IntegerPropertyTestCase(unittest.TestCase):
    def test_convert(self):
        entity = Model4()
        self.assertIsNone(entity.b)
        entity.b = 0
        self.assertEqual(entity.b, 0)
        entity.b = 1
        self.assertEqual(entity.b, 1)
        entity.b = -1
        self.assertEqual(entity.b, -1)
        entity.b = '2'
        self.assertEqual(entity.b, 2)
        entity.b = True
        self.assertEqual(entity.b, 1)
        entity.b = False
        self.assertEqual(entity.b, 0)
        entity.b = None
        self.assertIsNone(entity.b)
        entity.b = 1.2
        self.assertEqual(entity.b, 1)
        with self.assertRaises(ValueError):
            entity.b = ''
        with self.assertRaises(ValueError):
            entity.b = 'a'


class BooleanPropertyTestCase(unittest.TestCase):
    def test_convert(self):
        entity = Model4()
        self.assertIsNone(entity.c)
        entity.c = True
        self.assertEqual(entity.c, True)
        entity.c = False
        self.assertEqual(entity.c, False)
        entity.c = 1
        self.assertEqual(entity.c, True)
        entity.c = 0
        self.assertEqual(entity.c, False)
        entity.c = '2'
        self.assertEqual(entity.c, True)
        entity.c = ''
        self.assertEqual(entity.c, False)
        entity.c = 1.2
        self.assertEqual(entity.c, True)
        entity.c = []
        self.assertEqual(entity.c, False)
        entity.c = None
        self.assertIsNone(entity.c)


class FloatPropertyTestCase(unittest.TestCase):
    def test_convert(self):
        entity = Model4()
        self.assertIsNone(entity.d)
        entity.d = 0.0
        self.assertEqual(entity.d, 0.0)
        entity.d = 0.1
        self.assertAlmostEqual(entity.d, 0.1)
        entity.d = -1.2
        self.assertAlmostEqual(entity.d, -1.2)
        entity.d = True
        self.assertEqual(entity.d, 1.0)
        entity.d = False
        self.assertEqual(entity.d, 0.0)
        entity.d = 1
        self.assertEqual(entity.d, 1.0)
        entity.d = 0
        self.assertEqual(entity.d, 0.0)
        entity.d = '2'
        self.assertEqual(entity.d, 2.0)
        entity.d = '2.4'
        self.assertAlmostEqual(entity.d, 2.4)
        entity.d = None
        self.assertIsNone(entity.d)
        with self.assertRaises(ValueError):
            entity.d = ''
        with self.assertRaises(ValueError):
            entity.d = 'a'


class DateTimePropertyTestCase(unittest.TestCase):
    def test_convert(self):
        entity = Model4()
        self.assertIsNone(entity.e)
        entity.e = 0
        self.assertEqual(entity.e, 0)
        entity.e = 1
        self.assertEqual(entity.e, 1)
        entity.e = '2'
        self.assertEqual(entity.e, 2)
        entity.e = True
        self.assertEqual(entity.e, 1)
        entity.e = False
        self.assertEqual(entity.e, 0)
        entity.e = None
        self.assertIsNone(entity.e)
        entity.e = 1.2
        self.assertEqual(entity.e, 1)
        utcnow = datetime.utcnow()
        entity.e = utcnow
        self.assertEqual(entity.e, calendar.timegm(utcnow.utctimetuple()))
        with self.assertRaises(ValueError):
            entity.e = ''
        with self.assertRaises(ValueError):
            entity.e = 'a'
        with self.assertRaises(ValueError):
            entity.e = -1

        self.assertIsInstance(entity.f, int)
        self.assertLess(entity.e - entity.f, 2)
        entity.f = None
        self.assertLess(entity.f - entity.e, 2)
        entity.f = 1
        self.assertEqual(entity.f, 1)


class TuplePropertyTestCase(unittest.TestCase):
    def test_convert(self):
        entity = Model5()

        self.assertListEqual(entity.a, [])
        entity.a = ('1', u'囧')
        self.assertListEqual(entity.a, ['1', u'囧'])
        entity.a *= 2
        self.assertListEqual(entity.a, ['1', u'囧', '1', u'囧'])
        entity.a = []
        self.assertEqual(entity.a, [])
        entity.a = [0, None]
        self.assertListEqual(entity.a, [0, None])
        entity.a = {'1', '2'}
        self.assertItemsEqual(entity.a, ['1', '2'])
        entity.a = None
        self.assertListEqual(entity.a, [])

        with self.assertRaises(ValueError):
            entity.a = 0

        with self.assertRaises(ValueError):
            entity.a = '1'


if __name__ == '__main__':
    unittest.main()
