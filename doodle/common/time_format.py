# -*- coding: utf-8 -*-

import calendar
from datetime import datetime, timedelta, tzinfo
import re

from doodle.config import CONFIG


DATE_FORMAT = '%Y/%m/%d/'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ISO_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
ISO8601_TIME_FORMAT = '%Y%m%dT%H:%M:%SZ'

DATE_PATTERN = re.compile(r'(19\d{2}|2\d{3})/(0[1-9]|1[0-2])/([0-2]\d|3[01])/')

SECONDS_IN_A_DAY = 60 * 60 * 24

ZERO_TIME_DELTA = timedelta(0)
ONE_SECOND = timedelta(seconds=1)


class LocalTimezone(tzinfo):
    def utcoffset(self, dt):
        return CONFIG.LOCAL_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA


LOCAL_TIMEZONE = LocalTimezone()


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA


UTC_TIMEZONE = UTC()


def convert_to_local_time(dt):
    if dt.tzinfo:
        return dt.astimezone(LOCAL_TIMEZONE)
    else:
        return dt.replace(tzinfo=UTC_TIMEZONE).astimezone(LOCAL_TIMEZONE)


def parse_time(time_string):
    try:
        dt = datetime.strptime(time_string, TIME_FORMAT).replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC_TIMEZONE).replace(tzinfo=None)
        return dt if dt.year >= 1900 else None # the datetime strftime() method requires year >= 1900
    except Exception:
        return None


def get_local_now():
    return datetime.now(LOCAL_TIMEZONE)


def formatted_date(dt):
    return convert_to_local_time(dt).strftime(CONFIG.DATE_FORMAT)


def formatted_date_for_url(dt=None):
    if not dt:
        return get_local_now().strftime(DATE_FORMAT)
    return convert_to_local_time(dt).strftime(DATE_FORMAT)


def parse_date_for_url(date_string):
    match = DATE_PATTERN.match(date_string)
    if match:
        year, month, day = match.groups()
        year = int(year)
        month = int(month)
        day = int(day)
        try:
            return datetime(year, month, day)
        except ValueError:
            day = 1
            month += 1
            if month > 12:
                month = 12
                year += 1
            return datetime(year, month, day)


def formatted_time(dt, display_second=True):
    return convert_to_local_time(dt).strftime(CONFIG.SECONDE_FORMAT if display_second else CONFIG.MINUTE_FORMAT)


def formatted_time_for_edit(dt):
    return convert_to_local_time(dt).strftime(TIME_FORMAT)


def get_time(time, compare_time):
    if not time or not time.strip():
        return datetime.utcnow()
    else:
        time = parse_time(time)
        if time:
            if time == compare_time:
                return None
            elif time > compare_time:
                return time if (time - compare_time > ONE_SECOND) else None
            else:
                return time if (compare_time - time > ONE_SECOND) else None
        else:
            return None


def sitemap_time_format(dt):
    if dt.tzinfo:
        dt = dt.astimezone(UTC_TIMEZONE)
    return dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')


def iso_time_format(dt):
    if dt.tzinfo:
        return convert_to_local_time(dt).strftime(ISO_TIME_FORMAT)
    else:
        return dt.strftime(ISO_TIME_FORMAT)


def iso_time_now():
    return datetime.utcnow().strftime(ISO_TIME_FORMAT)


def parse_iso8601_time(time_string):
    return datetime.strptime(time_string, ISO8601_TIME_FORMAT)


def datetime_to_timestamp(dt):  # UTC datetime
    return calendar.timegm(dt.utctimetuple())


def timestamp_to_datetime(timestamp):  # UTC datetime
    return datetime.utcfromtimestamp(timestamp)


def time_from_now(time):
    if isinstance(time, int):
        time = timestamp_to_datetime(time)
    time_diff = datetime.utcnow() - time
    days = time_diff.days
    if days:
        if days > 365:
            return u'%s年前' % (days / 365)
        if days > 30:
            return u'%s月前' % (days / 30)
        if days > 7:
            return u'%s周前' % (days / 7)
        return u'%s天前' % days
    seconds = time_diff.seconds
    if seconds > 3600:
        return u'%s小时前' % (seconds / 3600)
    if seconds > 60:
        return u'%s分钟前' % (seconds / 60)
    return u'%s秒前' % seconds
