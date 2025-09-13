# -*- coding: utf-8 -*-

import locale
from datetime import datetime
import functools
import warnings
try:
    from collections.abc import Mapping, MutableMapping, Iterable
except ImportError:
    from collections import Mapping, MutableMapping, Iterable

import six


def get_tzlocal():
    try:
        tzlocal = datetime.now().astimezone().tzinfo
    except (ValueError, TypeError):
        from dateutil.tz import tzlocal
        tzlocal = tzlocal()
    return tzlocal


def format_rfc822(date):
    """

    Parameters
    ----------
    date : datetime
        Datetime object

    Returns
    -------
    str
        Stringified datetime object according to RFC 822 standard
    """
    orig_locale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    if not date.tzinfo:
        date = date.replace(tzinfo=get_tzlocal())
    date = date.strftime('%a, %d %b %Y %H:%M:%S %z')
    locale.setlocale(locale.LC_TIME, orig_locale)
    return date


def object_to_list(obj):
    """
    Wrap object to list.

    Parameters
    ----------
    obj
        Any object

    Returns
    -------
    list
        Falsy object is converted to empty list.
        Iterable object (excluding string) is wrapped to a list with multiple items.
        Otherwise, object is wrapped to a list with the single item.
    """
    if not obj:
        return []
    if not isinstance(obj, six.string_types) and isinstance(obj, Iterable):
        return list(obj)
    return [obj]


def is_strict_subclass(cls, base_cls):
    """
    Check if class is subclass of some derived class from given

    Parameters
    ----------
    cls
        Class object
    base_cls
        Potentially ancestor class object

    Returns
    -------
    bool
        Whether the ``cls`` is subclass of ``base_cls`` and they are not the same
    """
    return issubclass(cls, base_cls) and cls != base_cls


def get_full_class_name(cls):
    if not hasattr(cls, '__name__'):
        raise TypeError("object does not have __name__")
    fullname = cls.__qualname__ if hasattr(cls, '__qualname__') else cls.__name__
    if hasattr(cls, '__module__') and cls.__module__ not in ('builtins', '__builtin__'):
        fullname = cls.__module__ + '.' + fullname
    return fullname


def deprecated_class(reason):
    """
    Decorator which can be used to mark classes
    as deprecated. It will result in a warning being emitted
    when the class is used.
    """

    if not isinstance(reason, six.string_types):
        raise TypeError('Unsupported reason type: ' + repr(type(reason)))

    def decorator(wrapped):
        old_new1 = wrapped.__new__
        wrapped_name = wrapped.__name__

        def wrapped_cls(cls, *args, **kwargs):
            msg = "Class <{name}> is deprecated. {reason}".format(name=wrapped_name, reason=reason)
            warnings.simplefilter('always', DeprecationWarning)  # turn off filter
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)  # reset filter
            if old_new1 is object.__new__:
                return old_new1(cls)
            # actually, we don't know the real signature of *old_new1*
            return old_new1(cls, *args, **kwargs)

        wrapped.__new__ = staticmethod(wrapped_cls)

        return wrapped

    return decorator


def deprecated_func(reason):
    if not isinstance(reason, six.string_types):
        raise TypeError('Unsupported reason type: ' + repr(type(reason)))

    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)  # turn off filter
            warnings.warn(reason, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)  # reset filter
            return func(*args, **kwargs)
        return new_func
    return decorator


def deprecated_module(reason):
    warnings.simplefilter('always', DeprecationWarning)  # turn off filter
    warnings.warn(reason, category=DeprecationWarning, stacklevel=2)
    warnings.simplefilter('default', DeprecationWarning)  # reset filter
