# -*- coding: utf-8 -*-

import six
from scrapy.item import ItemMeta as BaseItemMeta, Item as BaseItem, MutableMapping

from ..utils import deprecated

try:
    from scrapy.item import _BaseItemMeta
except ImportError:
    _BaseItemMeta = type

from .element import Element, MultipleElements, ElementMeta


class ItemMeta(ElementMeta, BaseItemMeta):
    pass


class FeedItem(six.with_metaclass(ItemMeta, Element, BaseItem)):
    """
    Properties
    ----------
    elements : { NSComponentName : Element }
        All elements of the item
    """

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], MutableMapping):
            args[0].update(kwargs)
            kwargs = args[0]
            args = tuple()
        fields_kwargs = {}
        for key in list(kwargs):
            if key in self.fields:
                fields_kwargs[key] = kwargs[key]
                del kwargs[key]
        Element.__init__(self, *args, **kwargs)
        BaseItem.__init__(self, **fields_kwargs)

    @property
    def elements(self):
        return self._children

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


# Backward compatibility
@deprecated("Use FeedItem class instead")
class ExtendableItem(FeedItem):
    pass
