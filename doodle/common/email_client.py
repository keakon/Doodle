# -*- coding: utf-8 -*-

import logging
from urllib import urlencode

from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from tornado.gen import coroutine

from doodle.config import CONFIG


_MAILGUN_API_URL = CONFIG.MAILGUN_API_BASE_URL + '/messages'


@coroutine
def send_email(to, subject, html):
    if isinstance(to, unicode):
        to = to.encode('utf-8')
    if isinstance(subject, unicode):
        subject = subject.encode('utf-8')
    if isinstance(html, unicode):
        html = html.encode('utf-8')

    data = {
        'from': CONFIG.EMAIL_SENDER,
        'to': to,
        'subject': subject,
        'html': html
    }
    data = urlencode(data)
    request = HTTPRequest(
        url=_MAILGUN_API_URL,
        method='POST',
        auth_username='api',
        auth_password=CONFIG.MAILGUN_API_KEY,
        body=data
    )
    client = AsyncHTTPClient()
    try:
        yield client.fetch(request)
    except HTTPError as e:
        try:
            response = e.response.body
        except AttributeError:
            response = None
        logging.exception('failed to send email:\nto: %s\nsubject: %s\nhtml: %s\nresponse: %s', to, subject, html, response)
