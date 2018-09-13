# -*- coding: utf-8 -*-

from datetime import datetime
import time

from doodle.common.time_format import datetime_to_timestamp


class Property(object):
    def __init__(self, name=None):
        self.name = name

    def __get__(self, model_instance, model_class):
        if model_instance is None:
            return self
        return model_instance._attributes.get(self.name)

    def __set__(self, model_instance, value):
        value = self.validate(value)
        model_instance._attributes[self.name] = value

    def validate(self, value):
        return value

    def is_empty(self, value):
        return value is None


class StringProperty(Property):
    def validate(self, value):
        if value is None:
            return ''
        if not isinstance(value, basestring):
            value = str(value)
        return value

    def is_empty(self, value):
        return not value


class DateTimeProperty(Property):
    def __init__(self, auto_now=False, **kwargs):
        super(DateTimeProperty, self).__init__(**kwargs)
        self.auto_now = auto_now

    def validate(self, value):
        if value is not None:
            if isinstance(value, datetime):
                return datetime_to_timestamp(value)
            try:
                value = int(value)
            except ValueError:
                raise ValueError('Property %s must be a timestamp' % self.name)
            if value < 0:
                raise ValueError('Property %s must be non-negative' % self.name)
            return value
        if self.auto_now:
            return int(time.time())


class IntegerProperty(Property):
    def validate(self, value):
        if value is not None:
            try:
                return int(value)
            except ValueError:
                raise ValueError('Property %s must be an int or long, not a %s'
                                 % (self.name, value.__class__.__name__))


class FloatProperty(Property):
    def validate(self, value):
        if value is not None:
            try:
                return float(value)
            except ValueError:
                raise ValueError('Property %s must be a float' % self.name)


class BooleanProperty(Property):
    def validate(self, value):
        if value is not None:
            return bool(value)


class ListProperty(Property):
    def validate(self, value):
        if value is None:
            return []
        if not hasattr(value, '__iter__'):
            raise ValueError('Property %s must be iterable' % self.name)
        if not value:
            return []
        if isinstance(value, list):
            return value
        return list(value)

    def is_empty(self, value):
        return not value


class PropertiedClass(type):
    def __init__(cls, name, bases, dct):
        super(PropertiedClass, cls).__init__(name, bases, dct)

        if 'KEY' not in cls.__dict__:
            cls.KEY = cls.__name__

        if hasattr(cls, '_properties'):
            cls._properties = cls._properties.copy()
        else:
            cls._properties = {}  # stores Property instances

        for prop_name, prop in dct.iteritems():
            if isinstance(prop, Property):
                cls._properties[prop_name] = prop
                prop.name = prop_name
