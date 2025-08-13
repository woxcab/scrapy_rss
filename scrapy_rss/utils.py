# -*- coding: utf-8 -*-

import locale
import warnings

import six


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


def deprecated(reason):
    """
    Decorator which can be used to mark classes
    as deprecated. It will result in a warning being emitted
    when the class is used.
    """

    if not isinstance(reason, six.string_types):
        raise TypeError('Unsupported type: ' + repr(type(reason)))

    def decorator(wrapped):
        old_new1 = wrapped.__new__
        wrapped_name = wrapped.__name__

        def wrapped_cls(cls, *args, **kwargs):
            msg = "Class {name} is deprecated. {reason}".format(name=wrapped_name, reason=reason)
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            if old_new1 is object.__new__:
                return old_new1(cls)
            # actually, we don't know the real signature of *old_new1*
            return old_new1(cls, *args, **kwargs)

        wrapped.__new__ = staticmethod(wrapped_cls)

        return wrapped

    return decorator

def deprecated_module(reason):
    warnings.warn(reason, category=DeprecationWarning, stacklevel=2)
