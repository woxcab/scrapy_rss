# -*- coding: utf-8 -*-

import pytest
from datetime import datetime, timedelta
from itertools import product
from dateutil.tz import tzoffset

from scrapy_rss.utils import format_rfc822, deprecated_module, deprecated_class, deprecated_func


@pytest.mark.parametrize("dt,timezone_offset", product([
    datetime.now(),
    datetime(2000, 1, 1, 0, 0, 0),
    datetime(2010, 12, 28, 1, 1, 1),
    datetime(2020, 12, 28, 23, 59, 59),
], [
    -1, 0, -1, -10, 10
]))
def test_format_rfc822(dt, timezone_offset):
    tz = tzoffset('Etc/GMT{:+}'.format(timezone_offset), timedelta(hours=timezone_offset))
    dt = dt.replace(tzinfo=tz)
    weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dt.weekday()]
    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][dt.month-1]
    expected = ('{}, {:02} {} {} {:02}:{:02}:{:02} {:+03}00'
                .format(weekday, dt.day, month, dt.year,
                        dt.hour, dt.minute, dt.second, timezone_offset))
    assert format_rfc822(dt) == expected


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
