# -*- coding: utf-8 -*-

from copy import deepcopy
import six
from scrapy.item import ItemMeta as BaseItemMeta, Item as BaseItem, MutableMapping

try:
    from scrapy.item import _BaseItemMeta
except ImportError:  # pragma: no cover
    _BaseItemMeta = type

from ..exceptions import *
from .nscomponent import NSComponentName
from .element import ItemElement, MultipleElements


class ItemMeta(BaseItemMeta):
    def __new__(mcs, cls_name, cls_bases, cls_attrs):
        cls_attrs['_elements'] = {}
        for cls_base in reversed(cls_bases):
            if isinstance(cls_base, ItemMeta):
                cls_attrs['_elements'].update(cls_base._elements)
                for attr_name, attr_value in cls_base.__dict__.items():
                    if isinstance(attr_value, ItemElement):
                        cls_attrs[attr_name] = attr_value
        elements = {NSComponentName(elem_name, elem_descr.ns_prefix, elem_descr.ns_uri):
                    elem_descr for elem_name, elem_descr in cls_attrs.items()
                    if isinstance(elem_descr, ItemElement)}
        for elem_name, elem in elements.items():
            if not elem.ns_prefix:
                elem.ns_prefix = elem_name.ns_prefix
        cls_attrs['_elements'].update(elements)
        cls_attrs['elements'] = property(lambda self: self._elements)
        cls_attrs.update({elem_name.priv_name: elem_descriptor
                          for elem_name, elem_descriptor in elements.items()})
        cls_attrs.update({elem_name.pub_name: property(mcs.build_elem_getter(elem_name),
                                                       mcs.build_elem_setter(elem_name, elem_descr))
                          for elem_name, elem_descr in elements.items()})
        return super(ItemMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)

    @staticmethod
    def build_elem_getter(elem_name):
        return lambda self: getattr(self, elem_name.priv_name)

    @staticmethod
    def build_elem_setter(elem_name, elem_descriptor):
        def setter(self, new_value):
            if isinstance(elem_descriptor, MultipleElements):
                multi_elem = getattr(self, elem_name.priv_name)
                multi_elem.clear()
                multi_elem.add(new_value)
            elif isinstance(new_value, elem_descriptor.__class__):
                setattr(self, elem_name.priv_name, new_value)
            elif isinstance(new_value, dict):
                setattr(self, elem_name.priv_name, elem_descriptor.__class__(**new_value))
            elif not elem_descriptor.required_attrs and elem_descriptor.content_arg:
                elem = getattr(self, elem_name.priv_name)
                setattr(elem, elem_descriptor.content_arg.pub_name, new_value)
            else:
                raise InvalidElementValueError(elem_name, elem_descriptor.__class__, new_value)
        return setter


class FeedItem(six.with_metaclass(ItemMeta, BaseItem)):
    """
    Attributes
    ----------
    elements : { NSComponentName : ItemElement }
        All elements of the item
    """
    def __init__(self, *args, **kwargs):
        super(FeedItem, self).__init__(*args, **kwargs)
        new_elements = {}
        for elem_name, elem_descr in self._elements.items():
            new_element = deepcopy(getattr(self, elem_name.priv_name))
            setattr(self, elem_name.priv_name, new_element)
            new_elements[elem_name] = new_element
        self._elements = new_elements

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={!r}".format(elem_name, elem)
                      for elem_name, elem in self.elements.items()))

    def __setattr__(self, name, value):
        if name in self.fields:
            raise AttributeError("Use item[{!r}] = {!r} to set field value".format(name, value))
        super(MutableMapping, self).__setattr__(name, value)

    def get_namespaces(self, assigned_only=True):
        """
        Get all namespaces of the elements and its attributes

        Parameters
        ----------
        assigned_only : bool
            Whether to return namespaces of assigned components only

        Returns
        -------
        set of (str or None, str or None)
            Set of pairs (namespace_prefix, namespace_uri)
        """
        namespaces = set()
        for elem in self.elements.values():
            if not assigned_only or elem.assigned:
                namespaces.update(elem.get_namespaces(assigned_only))
        return namespaces


ExtendableItem = FeedItem  # Backward compatibility
