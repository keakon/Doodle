# -*- coding: utf-8 -*-

class Property(object):
    def __init__(self, fget):
        self.fget = fget
        self.__doc__ = fget.__doc__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError, 'unreadable attribute'
        return self.fget(obj)


class CachedProperty(Property):
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        fget = self.fget
        if fget is None:
            raise AttributeError, 'unreadable attribute'
        obj.__dict__[fget.__name__] = prop = fget(obj)
        return prop
