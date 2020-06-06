# -*- coding: utf-8 -*-

from copy import deepcopy

from ..exceptions import *
from .element import ItemElement, MultipleElements


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
