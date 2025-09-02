# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime, timedelta, tzinfo
from itertools import product
import pytest

from scrapy_rss.utils import format_rfc822, deprecated_module, deprecated_class, deprecated_func


@pytest.mark.parametrize("dt,timezone_offset", product([
    datetime.now(),
    datetime(2000, 1, 1, 0, 0, 0),
    datetime(2010, 12, 28, 1, 1, 1),
    datetime(2020, 12, 28, 23, 59, 59),
], [
    -10, -1, 0, 2, 10
]))
def test_format_rfc822(dt, timezone_offset):
    class TzOffset(tzinfo):
        def __init__(self, name, offset):
            self._name = name
            self._offset = timedelta(seconds=offset.total_seconds())

        def utcoffset(self, dt):
            return self._offset

        def dst(self, dt):
            return timedelta(0)

        def tzname(self, dt):
            return self._name

        def fromutc(self, dt):
            return dt + self._offset

    tz = TzOffset('Etc/GMT{:+}'.format(-timezone_offset), timedelta(hours=timezone_offset))
    dt = dt.replace(tzinfo=tz)
    weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dt.weekday()]
    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][dt.month-1]
    expected = ('{}, {:02} {} {} {:02}:{:02}:{:02} {:+03}00'
                .format(weekday, dt.day, month, dt.year,
                        dt.hour, dt.minute, dt.second, timezone_offset))
    assert format_rfc822(dt) == expected

@pytest.mark.parametrize("tz_offset,tz_name",
                         ((n, 'Etc/GMT{:+}'.format(-n) if abs(n) >= 10 or n == 0
                              else {-1: 'Atlantic/Cape_Verde', 2: 'Europe/Kaliningrad'}[n])
                          for n in  [-10, -1, 0, 2, 10]))
def test_tzlocal(tz_offset, tz_name):
    from scrapy_rss.utils import get_tzlocal

    old_os_tz = os.environ.get('TZ', None)
    try:
        os.environ['TZ'] = tz_name
        time.tzset()
        dt_tz = datetime.now(get_tzlocal())
        dt_naive = datetime.now()
        actual_offset = dt_tz.tzinfo.utcoffset(dt_naive)
        expected_offset = timedelta(seconds=60*60*tz_offset)
    finally:
        if old_os_tz:
            os.environ['TZ'] = old_os_tz
        else:
            del os.environ['TZ']
        time.tzset()
    assert actual_offset == expected_offset


def test_deprecated_module():
    with pytest.warns(DeprecationWarning):
        deprecated_module('Message')


def test_deprecated_class():
    @deprecated_class('Message')
    class A(object):
        pass

    with pytest.warns(DeprecationWarning):
        A()

    with pytest.raises(TypeError, match='Unsupported reason type'):
        @deprecated_class
        class B:
            pass


def test_deprecated_func():
    @deprecated_func('Message')
    def func_a():
        pass

    with pytest.warns(DeprecationWarning):
        func_a()

    with pytest.raises(TypeError, match='Unsupported reason type'):
        @deprecated_func
        def func_b():
            pass


if __name__ == '__main__':
    pytest.main()
