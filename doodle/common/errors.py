# -*- coding: utf-8 -*-


class BaseError(Exception):
    def __init__(self, message=None, *args, **kwargs):
        super(BaseError, self).__init__(message, *args)
        if kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)


class PropertyError(BaseError):
    pass


class IntegrityError(BaseError):
    pass
