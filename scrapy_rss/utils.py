# -*- coding: utf-8 -*-

import locale


def format_rfc822(date):
    l = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    date = date.strftime('%a, %d %b %Y %H:%M:%S %z')
    locale.setlocale(locale.LC_TIME, l)
    return date
