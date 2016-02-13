# -*- coding: utf-8 -*-

import os


doodle_env = os.getenv('DOODLE_ENV')
try:
    if doodle_env == 'PRODUCTION':
        from .production import ProductionConfig as CONFIG
    elif doodle_env == 'TEST':
        from .test import TestConfig as CONFIG
    else:
        from .development import DevelopmentConfig as CONFIG
except ImportError:
    import logging
    logging.warning('Loading config for %s environment failed, use default config instead.', doodle_env or 'unspecified')

    from .default import Config as CONFIG
