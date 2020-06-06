# -*- coding: utf-8 -*-

import locale


def format_rfc822(date):
    """

    Parameters
    ----------
    date : datetime.datetime
        Datetime object

    Returns
    -------
    str
        Stringified datetime object according to RFC 822 standard
    """
    orig_locale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    date = date.strftime('%a, %d %b %Y %H:%M:%S %z')
    locale.setlocale(locale.LC_TIME, orig_locale)
    return date
