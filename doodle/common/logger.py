# -*- coding: utf-8 -*-

import logging
import sys


LOGGING_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%y%m%d %H:%M:%S'

logging.basicConfig(
    level=logging.INFO,
    format=LOGGING_FORMAT,
    datefmt=DATE_FORMAT,
    stream=sys.__stdout__
)

root_logger = logging.getLogger()

stderr_handler = logging.StreamHandler(sys.__stderr__)
stderr_handler.level = logging.ERROR
stderr_handler.formatter = logging.Formatter(LOGGING_FORMAT, DATE_FORMAT)
root_logger.addHandler(stderr_handler)
