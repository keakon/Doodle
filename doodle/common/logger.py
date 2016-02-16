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

from tornado.log import access_log

def log_request(handler):
    try:
        request = handler.request
        location_info = referer_info = user_agent_info = ''
        status_code = handler.get_status()
        if status_code < 400:
            log_method = access_log.info
            if status_code in (301, 302, 307):
                location = handler._headers.get('Location')
                if location:
                    location_info = '\n\tLocation: ' + location
        elif status_code < 500:
            log_method = access_log.warning
            headers = request.headers
            referer = headers.get('Referer')
            if referer:
                referer = referer.replace('"', '')
                referer_info = '\n\tReferer url: ' + referer
            user_agent = headers.get('User-Agent')
            if user_agent:
                user_agent = user_agent.replace('"', '')
                user_agent_info = '\n\tUser agent: ' + user_agent
        else:
            log_method = access_log.error

        request_time = request.request_time()
        log_method("%d %s %.2fms%s%s%s", status_code,
                   handler._request_summary(), request_time * 1000.0,
                   location_info, referer_info, user_agent_info)
    except Exception:
        logging.exception('failed to log request')
