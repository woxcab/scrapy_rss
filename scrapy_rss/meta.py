# -*- coding: utf-8 -*-

from copy import deepcopy
import six
from scrapy_rss.exceptions import *


class ItemElementAttribute:
    def __init__(self, value=None, serializer=lambda x: str(x), required=False, is_content=False):
        self.__required = required
        self.__is_content = is_content
        self.serializer = serializer
        self.value = value

    @property
    def required(self):
        return self.__required

    @property
    def is_content(self):
        return self.__is_content


class ItemElementMeta(type):
    def __new__(mcs, cls_name, cls_bases, cls_attrs):
        elem_attrs = {attr_name: attr_descriptor for attr_name, attr_descriptor in cls_attrs.items()
                      if isinstance(attr_descriptor, ItemElementAttribute)}
        assert sum(attr.is_content for attr in elem_attrs.values()) <= 1
        cls_attrs['_attrs'] = elem_attrs

        cls_attrs.update({'__{}'.format(attr_name): attr_descriptor
                          for attr_name, attr_descriptor in elem_attrs.items()})
        cls_attrs.update({attr_name: property(mcs.build_attr_getter(attr_name),
                                              mcs.build_attr_setter(attr_name))
                          for attr_name in elem_attrs})

        return super(ItemElementMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)

    def __init__(cls, cls_name, cls_bases, cls_attrs):
        cls.assigned = False
        cls.attrs = property(lambda self: self._attrs)

        cls._required_attrs = {attr_name: attr_descriptor
                               for attr_name, attr_descriptor in cls._attrs.items()
                               if attr_descriptor.required and not attr_descriptor.is_content}
        cls.required_attrs = property(lambda self: self._required_attrs)

        content_arg = [attr_name for attr_name, attr_descriptor in cls._attrs.items()
                        if attr_descriptor.is_content]
        cls._content_arg = content_arg[0] if content_arg else None
        cls.content_arg = property(lambda self: self._content_arg)

        cls.serialize = lambda self: {attr_name: attr.serializer(getattr(self, attr_name))
                                      for attr_name in self.attrs
                                      for attr in (getattr(self, '__{}'.format(attr_name)),)
                                      if attr.value is not None}

        super(ItemElementMeta, cls).__init__(cls_name, cls_bases, cls_attrs)

    @staticmethod
    def build_attr_getter(attr_name):
        return lambda self: getattr(self, '__{}'.format(attr_name)).value

    @staticmethod
    def build_attr_setter(attr_name):
        def setter(self, value):
            attr = getattr(self, '__{}'.format(attr_name))
            attr.value = value
            self.assigned = True
        return setter


@six.add_metaclass(ItemElementMeta)
class ItemElement:
    def __init__(self, *args, **kwargs):
        if not self.content_arg and args:
            raise ValueError("Element of type '{}' does not support unnamed arguments (no content)".format(self.__class__.__name__))
        if len(args) > 1:
            raise ValueError("Constructor of class '{}' supports only single unnamed argument "
                             "that is interpreted as content of element".format(self.__class__.__name__))
        if not set(kwargs.keys()) <= set(self.attrs.keys()):
            raise ValueError("Passed arguments {}. But constructor of class '{}' supports only the next named arguments: {}"
                             .format(list(kwargs.keys()), self.__class__.__name__, list(self.attrs)))

        if args and self.content_arg not in kwargs:
            kwargs[self.content_arg] = args[0]
        for attr_name in self._attrs:
            setattr(self, '__{}'.format(attr_name), deepcopy(getattr(self, '__{}'.format(attr_name))))

        for attr_name, attr_value in kwargs.items():
            setattr(self, attr_name, attr_value)

    def is_valid(self):
        return (not self.assigned
                or all(getattr(self, attr_name) is not None for attr_name in self.required_attrs)
                    and (not self.content_arg or not self.attrs[self.content_arg].required
                         or getattr(self, self.content_arg) is not None))


class MultipleElements(ItemElement):
    def __init__(self, base_element_cls):
        super(MultipleElements, self).__init__()
        if not isinstance(base_element_cls, ItemElementMeta):
            raise TypeError("Invalid type of elements class: {}".format(base_element_cls))
        self.base_element_cls = base_element_cls
        self.elements = []
        self._content_arg = base_element_cls._content_arg

        def serializer():
            raise NotImplementedError('Class MultipleElements does not support serialization')
        self.serialize = serializer

    def _check_value(self, value, name=None):
        if isinstance(value, self.base_element_cls):
            return value
        if isinstance(value, dict):
            return self.base_element_cls(**value)
        return self.base_element_cls(**{name: value}) if name else self.base_element_cls(value)

    def append(self, elem):
        self.elements.append(self._check_value(elem))
        self.assigned = True

    def extend(self, iterable):
        for elem in iterable:
            self.append(elem)

    def add(self, value):
        if isinstance(value, list):
            self.extend(value)
        else:
            self.append(value)

    def clear(self):
        del self.elements[:]
        self.assigned = False

    def pop(self, index=-1):
        elem = self.elements.pop(index)
        if not self.elements:
            self.assigned = False
        return elem

    def __delitem__(self, index):
        self.elements.__delitem__(index)
        if not self.elements:
            self.assigned = False

    def __getitem__(self, index):
        return self.elements[index]

    def __iter__(self):
        return iter(self.elements)

    def __len__(self):
        return len(self.elements)

    def __setitem__(self, index, elem):
        if not isinstance(elem, self.base_element_cls):
            raise TypeError("Elements must have type '{}' or descendant type, not '{}'"
                            .format(self.base_element_cls, elem.__class__))
        self.elements[index] = elem

    def __getattr__(self, name):
        if name == 'base_element_cls':
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))
        if name not in self.base_element_cls._attrs:
            raise AttributeError("Elements of type '{}' does not have '{}' attribute"
                                 .format(self.base_element_cls, name))
        if not self.elements:
            raise AttributeError("Instances of '{}' have not been assigned"
                                 .format(self.base_element_cls.__name__))
        if len(self.elements) > 1:
            raise AttributeError("Cannot get attribute: more than one elements have been assigned. "
                                 "Choose element and get its' attribute.")
        return getattr(self.elements[0], name)

    def __setattr__(self, name, value):
        if name != 'base_element_cls' and name in self.base_element_cls._attrs:
            if len(self.elements) != 1:
                raise AttributeError("Cannot set attribute: zero or more than one elements have been assigned. "
                                     "Choose element and set its' attribute.")
            setattr(self.elements[0], name, value)
        else:
            return super(MultipleElements, self).__setattr__(name, value)


class ItemMeta(type):
    def __new__(mcs, cls_name, cls_bases, cls_attrs):
        elements = {elem_name: elem_descriptor for elem_name, elem_descriptor in cls_attrs.items()
                    if isinstance(elem_descriptor, ItemElement)}
        cls_attrs['__elements'] = elements
        cls_attrs['elements'] = property(lambda self: getattr(self, '__elements'))
        cls_attrs.update({'__{}'.format(elem_name): elem_descriptor
                          for elem_name, elem_descriptor in elements.items()})
        cls_attrs.update({elem_name: property(mcs.build_elem_getter(elem_name),
                                              mcs.build_elem_setter(elem_name, elem_descriptor))
                          for elem_name, elem_descriptor in elements.items()})
        cls_attrs['__init__'] = mcs.build_elem_init()
        return super(ItemMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)

    @staticmethod
    def build_elem_init():
        def init(self):
            for elem_name in self.elements:
                setattr(self, '__{}'.format(elem_name), deepcopy(getattr(self, '__{}'.format(elem_name))))
        return init

    @staticmethod
    def build_elem_getter(elem_name):
            return lambda self: getattr(self, '__{}'.format(elem_name))

    @staticmethod
    def build_elem_setter(elem_name, elem_descriptor):
        def setter(self, new_value):
            if isinstance(elem_descriptor, MultipleElements):
                multi_elem = getattr(self, '__{}'.format(elem_name))
                multi_elem.clear()
                multi_elem.add(new_value)
            elif isinstance(new_value, elem_descriptor.__class__):
                setattr(self, '__{}'.format(elem_name), new_value)
            elif isinstance(new_value, dict):
                setattr(self, '__{}'.format(elem_name), elem_descriptor.__class__(**new_value))
            elif not elem_descriptor.required_attrs and elem_descriptor.content_arg:
                elem = getattr(self, '__{}'.format(elem_name))
                setattr(elem, elem_descriptor.content_arg, new_value)
            else:
                raise InvalidElementValueError(elem_name, elem_descriptor.__class__, new_value)
        return setter
