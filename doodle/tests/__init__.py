# -*- coding: utf-8 -*-

from doodle.config import CONFIG


if not CONFIG.TEST:
    raise EnvironmentError('cannot execute unit testing in current environment')
