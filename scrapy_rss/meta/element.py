# -*- coding: utf-8 -*-

from copy import deepcopy
import re
from itertools import chain

import six

from .meta_utils import _build_component_setter
from .attribute import ElementAttribute
from .nscomponent import BaseNSComponent, NSComponentName
from ..exceptions import InvalidElementValueError
from ..utils import deprecated


class ElementMeta(type):
    def __new__(mcs, cls_name, cls_bases, cls_attrs):
        elem_attrs = {NSComponentName(attr_name, ns_prefix=attr_descr.ns_prefix, ns_uri=attr_descr.ns_uri):
                      attr_descr for attr_name, attr_descr in cls_attrs.items()
                      if isinstance(attr_descr, ElementAttribute)}
        for attr_name, attr in elem_attrs.items():
            if not attr.ns_prefix:
                attr.ns_prefix = attr_name.ns_prefix
        if sum(attr.is_content for attr in elem_attrs.values()) > 1:
            raise ValueError("More than one attributes that's interpreted as content in the element '{}' specification"
                             .format(cls_name))
        cls_attrs['_attrs'] = elem_attrs

        children = {NSComponentName(elem_name, ns_prefix=elem_descr.ns_prefix, ns_uri=elem_descr.ns_uri):
                    elem_descr for elem_name, elem_descr in cls_attrs.items()
                    if isinstance(elem_descr.__class__, ElementMeta)}
        for elem_name, elem in children.items():
            if not elem.ns_prefix:
                elem.ns_prefix = elem_name.ns_prefix
        cls_attrs['_children'] = children

        cls_attrs.update({comp_name.priv_name: comp_descr
                          for comp_name, comp_descr in chain(elem_attrs.items(), children.items())})
        cls_attrs.update({comp_name.pub_name:
                          property(mcs.build_component_getter(comp_name),
                                   _build_component_setter(comp_name))
                          for comp_name in chain(elem_attrs, children)})

        return super(ElementMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)

    def __init__(cls, cls_name, cls_bases, cls_attrs):
        cls._assigned = False
        cls.assigned = property(
            lambda self: self._assigned or any(child.assigned for child in self._children.values())
        )
        cls.attrs = property(lambda self: self._attrs) # Attributes dict
        cls.children = property(lambda self: self._children) # children elements dict

        cls._required_attrs = {attr_name
                               for attr_name, attr_descr in cls._attrs.items()
                               if attr_descr.required and not attr_descr.is_content}
        cls.required_attrs = property(lambda self: self._required_attrs)

        cls._content_arg = None
        for attr_name, attr_descr in cls._attrs.items():
            if attr_descr.is_content:
                cls._content_arg = attr_name
                break
        cls.content_arg = property(lambda self: self._content_arg)

        cls.serialize_attrs = lambda self: {
            attr_name.xml_name: attr.serializer(attr.value)
            for attr_name in self.attrs
            for attr in (getattr(self, attr_name.priv_name),)
            if attr.assigned
        }

        super(ElementMeta, cls).__init__(cls_name, cls_bases, cls_attrs)

    @staticmethod
    def build_component_getter(name):
        """
        Build attribute getter

        Parameters
        ----------
        name : NSComponentName
            name of an attribute or child element
        """
        def getter(self):
            component = getattr(self, name.priv_name)
            return component.value if isinstance(component, ElementAttribute) else component
        return getter


@six.add_metaclass(ElementMeta)
class Element(BaseNSComponent):
    """
    Base class for elements

    Attributes
    ----------
    attrs : {NSComponentName : ElementAttribute}
        All attributes of the element
    children : {NSComponentName : Element}
        All children elements of this element
    required_attrs : set of NSComponentName
        Required element attributes excluding content attribute
    content_arg : NSComponentName or None
        Name of an attribute that's interpreted as the element content
    assigned : bool
        Whether a non-None value is assigned to any attribute or child element of this element

    Methods
    -------
    serialize_attrs() : { (str or None, str) : str }
        Convert values of element attributes to a strings.
        The dictionary key is a tuple (namespace_uri, attribute_name) for SAX handlers
    """

    def __init__(self, *args, **kwargs):
        if not self.content_arg and args:
            raise ValueError("Element of type '{}' does not support unnamed arguments (no content)"
                             .format(self.__class__.__name__))
        if len(args) > 1:
            raise ValueError("Constructor of class '{}' supports only single unnamed argument "
                             "that is interpreted as content of element".format(self.__class__.__name__))

        if args and str(self.content_arg) not in kwargs:
            kwargs[str(self.content_arg)] = args[0]

        new_attrs = {}
        new_children = {}
        for component_name in chain(self._attrs, self._children):
            new_component = deepcopy(getattr(self, component_name.priv_name))
            setattr(self, component_name.priv_name, new_component)
            if isinstance(new_component, ElementAttribute):
                new_attrs[component_name] = new_component
            else:
                new_children[component_name] = new_component
        self._attrs = new_attrs
        self._children = new_children

        for component_name in chain(self._attrs, self._children):
            component_name = str(component_name)
            if component_name in kwargs:
                setattr(self, component_name, kwargs[component_name])
                del kwargs[component_name]

        try:
            super(Element, self).__init__(**kwargs)
        except TypeError:
            raise ValueError("Passed arguments {}. "
                             "But constructor of class '{}' supports only the next named arguments: {}"
                             .format(list(kwargs.keys()), self.__class__.__name__,
                                     [str(a) for a in chain(self.attrs, self.children)]))

    def __repr__(self):
        s_match = re.match(r'^[^(]+\((.*?)\)$', super(Element, self).__repr__())
        s_repr = s_match.group(1) if s_match else ''
        comps_repr = ", ".join("{}={!r}".format(comp_name, comp)
                               for comp_name, comp in chain(self.attrs.items(),
                                                            self.children.items()))
        return "{}({})".format(self.__class__.__name__, ", ".join(filter(None, [comps_repr, s_repr])))

    def is_valid(self):
        """
        Check if the element has valid attributes' and children values.
        If this element is not assigned (skipped) then element is valid
        """
        return (
            not self.assigned
            or all(getattr(self, str(attr_name)) is not None for attr_name in self.required_attrs)
                and (not self.content_arg or not self.attrs[self.content_arg].required
                     or getattr(self, str(self.content_arg)) is not None)
                and all(child.is_valid() for child in self._children.values())
        )

    def get_namespaces(self, assigned_only=True):
        namespaces = super(Element, self).get_namespaces()
        for comp in chain(self.attrs.values(), self.children.values()):
            if not assigned_only or comp.assigned:
                namespaces.update(comp.get_namespaces(assigned_only))
        return namespaces


class MultipleElements(Element):
    """
    Represents elements of the same base class
    """

    def __init__(self, base_element_cls, **kwargs):
        if not isinstance(base_element_cls, ElementMeta):
            raise TypeError("Invalid type of elements class: {}".format(base_element_cls))
        self.base_element_cls = base_element_cls
        super(MultipleElements, self).__init__(**kwargs)
        self.elements = []
        self._kwargs = kwargs
        self._content_arg = base_element_cls._content_arg

        def serializer():
            raise NotImplementedError('Class MultipleElements does not support serialization')
        self.serialize = serializer

    def _check_value(self, value):
        if not self._kwargs.get("ns_prefix") and self.ns_prefix:
            self._kwargs["ns_prefix"] = self.ns_prefix
        if isinstance(value, self.base_element_cls):
            if self._kwargs.get("ns_uri") and not value.ns_uri:
                value.ns_uri = self._kwargs["ns_uri"]
            if not value.ns_prefix and self.ns_prefix:
                value.ns_prefix = self.ns_prefix
            return value
        if isinstance(value, dict):
            kwargs = self._kwargs.copy()
            kwargs.update(value)
            elem = self.base_element_cls(**kwargs)
            return elem
        return self.base_element_cls(value, **self._kwargs)

    def append(self, elem):
        """
        Append new element

        Parameters
        ----------
        elem : Element or { str : Any }
            New element as element instance or dictionary of attributes' values
        """
        self.elements.append(self._check_value(elem))
        self._assigned = True

    def extend(self, iterable):
        """
        Add multiple elements

        Parameters
        ----------
        iterable : iterable of (Element or { str : Any })
            Iterable of elements as element instances or dictionaries of attributes' values
        """
        for elem in iterable:
            self.append(elem)

    def add(self, value):
        """
        Add element(s) by value

        Parameters
        ----------
        value : Element or { str : Any } or iterable of (Element or { str : Any })
            New element(s) as element instance(s) or dictionary(-ies) of attributes' values
        """
        if isinstance(value, list):
            self.extend(value)
        else:
            self.append(value)

    def clear(self):
        """
        Remove all elements
        """
        del self.elements[:]
        self._assigned = False

    def pop(self, index=-1):
        """
        Remove single element

        Parameters
        ----------
        index : int
            Element index (last by default)
        """
        elem = self.elements.pop(index)
        if not self.elements:
            self._assigned = False
        return elem

    def __delitem__(self, index):
        self.elements.__delitem__(index)
        if not self.elements:
            self._assigned = False

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
        if name not in {attr.pub_name for attr in self.base_element_cls._attrs}:
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
        if name != 'base_element_cls' and name in {attr.pub_name for attr in self.base_element_cls._attrs}:
            if len(self.elements) != 1:
                raise AttributeError("Cannot set attribute: {} elements have been assigned. "
                                     "Choose element and set its' attribute.".format(len(self.elements)))
            setattr(self.elements[0], name, value)
        else:
            return super(MultipleElements, self).__setattr__(name, value)

    def __repr__(self):
        s_match = re.match(r'^[^(]+\((.*?)\)$', super(MultipleElements, self).__repr__())
        s_repr = s_match.group(1) if s_match else ''
        base_cls_repr = "base_element_cls={!r}".format(self.base_element_cls)
        return "{}({})".format(self.__class__.__name__, ", ".join(filter(None, [base_cls_repr, s_repr])))

    def get_namespaces(self, assigned_only=True):
        namespaces = super(MultipleElements, self).get_namespaces()
        for elem in self.elements:
            namespaces.update(elem.get_namespaces(assigned_only))
        return namespaces


# backward compatibility
@deprecated("Use ElementMeta class instead")
class ItemElementMeta(ElementMeta):
    pass

@deprecated("Use Element class instead")
class ItemElement(Element):
    pass
