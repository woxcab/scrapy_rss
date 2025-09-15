# -*- coding: utf-8 -*-

from copy import deepcopy
import re
from itertools import chain

import six

from .attribute import ElementAttribute
from .nscomponent import BaseNSComponent, NSComponentName
from ..exceptions import InvalidComponentNameError, InvalidComponentError, InvalidElementValueError, InvalidAttributeValueError
from ..utils import Mapping, Iterable, object_to_list, deprecated_class, deprecated_func


class ElementMeta(type):
    _blacklisted_comp_names = frozenset((
        '_attrs', 'attrs', '_children', 'children', '_required_attrs', 'required_attrs',
        '_required_children', 'required_children', '_content_name', 'content_name',
        '_required', 'required', '_assigned', 'assigned', 'base_element_cls'
    ))

    def __new__(mcs, cls_name, cls_bases, cls_attrs):
        for comp_name, comp_value in cls_attrs.items():
            if isinstance(comp_value, ElementAttribute) or isinstance(comp_value.__class__, ElementMeta):
                mcs._check_name(comp_name)

        cls_attrs['_attrs'] = {}
        cls_attrs['_children'] = {}
        for cls_base in reversed(cls_bases):
            if isinstance(cls_base, ElementMeta):
                cls_attrs['_attrs'].update(cls_base._attrs)
                cls_attrs['_children'].update(cls_base._children)
                for comp_name, comp_value in cls_base.__dict__.items():
                    if (isinstance(comp_value.__class__, ElementMeta)
                            or isinstance(comp_value, ElementAttribute)):
                        cls_attrs[comp_name] = comp_value
        elem_attrs = {NSComponentName(attr_name, ns_prefix=attr_descr.ns_prefix, ns_uri=attr_descr.ns_uri):
                      attr_descr for attr_name, attr_descr in cls_attrs.items()
                      if isinstance(attr_descr, ElementAttribute) and not attr_name.startswith('__')}
        for attr_name, attr in elem_attrs.items():
            if not attr.ns_prefix:
                attr.ns_prefix = attr_name.ns_prefix
        if sum(attr.is_content for attr in elem_attrs.values()) > 1:
            raise ValueError("More than one attributes that's interpreted as content in the element '{}' specification"
                             .format(cls_name))
        cls_attrs['_attrs'].update(elem_attrs)

        children = {NSComponentName(elem_name, ns_prefix=elem_descr.ns_prefix, ns_uri=elem_descr.ns_uri):
                    elem_descr for elem_name, elem_descr in cls_attrs.items()
                    if isinstance(elem_descr.__class__, ElementMeta) and not elem_name.startswith('__')}
        for elem_name, elem in children.items():
            if not elem.ns_prefix:
                elem.ns_prefix = elem_name.ns_prefix
        cls_attrs['_children'].update(children)

        cls_attrs.update({comp_name.priv_name: comp_descr
                          for comp_name, comp_descr in chain(elem_attrs.items(), children.items())})
        cls_attrs.update({comp_name.pub_name:
                          property(_build_component_getter(comp_name),
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
                               if attr_descr.required}
        cls.required_attrs = property(lambda self: self._required_attrs)
        cls._required_children = {elem_name
                                  for elem_name, elem_descr in cls._children.items()
                                  if elem_descr.required}
        cls.required_children = property(lambda self: self._required_children)

        cls._content_name = None
        for attr_name, attr_descr in cls._attrs.items():
            if attr_descr.is_content:
                cls._content_name = attr_name
                break
        cls.content_name = property(lambda self: self._content_name)
        # backward compatibility
        cls.content_arg = property(
            deprecated_func('Property <content_arg> is deprecated, use property <content_name> instead.')
                (lambda self: self._content_name)
        )

        cls.serialize_attrs = lambda self: {
            attr_name.xml_name: attr.serializer(attr.value)
            for attr_name in self.attrs
            for attr in (getattr(self, attr_name.priv_name),)
            if attr.assigned
        }

        super(ElementMeta, cls).__init__(cls_name, cls_bases, cls_attrs)

    @classmethod
    def _check_name(mcs, name):
        if name in mcs._blacklisted_comp_names:
            raise InvalidComponentNameError(name)
        return name


@six.add_metaclass(ElementMeta)
class Element(BaseNSComponent):
    """
    Base class for elements

    Properties
    ----------
    attrs : {NSComponentName : ElementAttribute}
        All attributes of the element.
    children : {NSComponentName : Element}
        All children elements of this element.
    required_attrs : set of NSComponentName
        Required element attributes.
    required_children : set of NSComponentName
        Required element children elements.
    content_name : NSComponentName or None
        Name of an attribute that's interpreted as the element content.
    required : bool
        Whether this element is required.
    assigned : bool
        Whether a non-None value is assigned to any attribute or child element of this element.

    Methods
    -------
    serialize_attrs() : { (str or None, str) : str }
        Convert values of element attributes to a strings.
        The dictionary key is a tuple (namespace_uri, attribute_name) for SAX handlers
    """

    _inited = False

    def __new__(cls, *args, **kwargs):
        instance = super(Element, cls).__new__(cls)
        new_attrs = {}
        new_children = {}
        for component_name in chain(instance._attrs, instance._children):
            new_component = deepcopy(getattr(instance, component_name.priv_name))
            Element.__setattr__(instance, component_name.priv_name, new_component)
            if isinstance(new_component, ElementAttribute):
                new_attrs[component_name] = new_component
            else:
                new_children[component_name] = new_component
        Element.__setattr__(instance, '_attrs', new_attrs)
        Element.__setattr__(instance, '_children', new_children)
        return instance

    def __init__(self, *args, **kwargs):
        """
        Initialize element

        Parameters
        ----------
        *args
            Content value if this element has a content attribute,
            or dict of attributes and children values
        **kwargs
            Named attributes and children values
        required : bool, optional
            Whether this element is required
        """
        if len(args) > 1:
            raise ValueError("Constructor of class '{}' supports only single unnamed argument "
                             "that is interpreted as content of this element or its child"
                             .format(self.__class__.__name__))
        self._required = kwargs.pop('required', False)
        if args:
            arg = args[0]
            if isinstance(arg, Element):
                raise NotImplementedError("Initialization from another <Element> instance is not supported")
            if isinstance(arg, Mapping):
                new_dict = {k: v for k, v in arg.items()}
                new_dict.update(kwargs)
                kwargs = new_dict
            elif self.content_name:
                if str(self.content_name) not in kwargs:
                    kwargs[str(self.content_name)] = arg
            elif not self._attrs and len(self._children) == 1:
                kwargs[str(next(iter(self._children)))] = arg
            else:
                raise ValueError("Element of type '{}' does not support unnamed non-mapping arguments "
                                 "(no content attribute, another attribute exists or no single child)"
                                 .format(self.__class__.__name__))
            args = tuple()

        for component_name in chain(self._attrs, self._children):
            component_name = str(component_name)
            if component_name in kwargs:
                setattr(self, component_name, kwargs[component_name])
                del kwargs[component_name]

        try:
            super(Element, self).__init__(**kwargs)
        except TypeError:
            raise KeyError("Element does not support components: {}. "
                           "Constructor of class '{}' supports only the next named arguments: {}"
                           .format(list(kwargs.keys()), self.__class__.__name__,
                                   [str(a) for a in chain(self.attrs, self.children)]))
        self._inited = True

    @property
    def required(self):
        return self._required

    @property
    def settings(self):
        settings = super(Element, self).settings
        settings['required'] = self._required
        return settings

    def __setattr__(self, key, value):
        if self._inited and not hasattr(self, key):
            raise AttributeError("No attribute {!r}. Supported components: {}"
                                 .format(key,
                                         ', '.join(map(repr, map(str, chain(self.attrs, self.children))))))
        super(Element, self).__setattr__(key, value)

    def __repr__(self):
        super_repr = super(Element, self).__repr__()
        if not hasattr(self, 'attrs') or not hasattr(self, 'children') or not hasattr(self, '_required'):
            return super_repr
        s_match = re.match(r'^[^(]+\((.*?)\)$', super_repr)
        s_repr = s_match.group(1) if s_match else ''
        comps_repr = ", ".join("{}={!r}".format(comp_name, comp)
                               for comp_name, comp in chain(self.attrs.items(),
                                                            self.children.items()))
        return "{}(required={!r}, {})".format(self.__class__.__name__,
                                              self._required,
                                              ", ".join(filter(None, [comps_repr, s_repr])))

    def clear(self):
        """
        Clear attributes and all children elements
        """
        for comp in chain(self.attrs.values(), self.children.values()):
            comp.clear()
        self._assigned = False

    def validate(self, name=None):
        """
        Check if the element has valid attributes' and children values.
        If this element is not assigned (skipped) and is not required then element is valid

        Parameters
        ----------
        name: str or NSComponentName or Iterable[str or NSComponentName] or None
            Name path of component

        Raises
        ------
        InvalidComponentError
            If this component is invalid
        """
        super(Element, self).validate(name)
        if not self.assigned:
            if self.required:
                raise InvalidComponentError(self, name, "missing required element")
            return
        for comp_name, comp in chain(self._attrs.items(), self._children.items()):
            name_path = object_to_list(name)
            name_path.append(comp_name)
            comp.validate(name_path)

    def get_namespaces(self, assigned_only=True, attrs_only=False):
        """
        Get namespaces of the element

        Parameters
        ----------
        assigned_only : bool
            whether return namespaces of assigned attributes and children only
        attrs_only
            whether return namespaces of assigned attributes only (skip children)

        Returns
        -------
        set of (str or None, str or None)
            Set of pairs (namespace_prefix, namespace_uri)
        """
        namespaces = super(Element, self).get_namespaces()
        for comp in chain(self.attrs.values(),
                          self.children.values() if not attrs_only else []):
            if not assigned_only or comp.assigned:
                namespaces.update(comp.get_namespaces(assigned_only))
        return namespaces


class MultipleElements(Element):
    """
    Represents sibling elements of the same base class
    """

    def __init__(self, base_element_cls, **kwargs):
        if not isinstance(base_element_cls, ElementMeta):
            raise TypeError("Invalid type of elements class: {}".format(base_element_cls))
        self.base_element_cls = base_element_cls
        super(MultipleElements, self).__init__(**kwargs)
        self._inited = False
        self.elements = []
        self._kwargs = kwargs
        self._content_name = base_element_cls._content_name
        self._inited = True

        def serializer():
            raise NotImplementedError('Class MultipleElements does not support attributes serialization')
        self.serialize_attrs = serializer

    @property
    def settings(self):
        settings = super(MultipleElements, self).settings
        settings['base_element_cls'] = self.base_element_cls
        return settings

    def _check_value(self, value):
        if not self._kwargs.get("ns_prefix") and self.ns_prefix:
            self._kwargs["ns_prefix"] = self.ns_prefix
        if isinstance(value, self.base_element_cls):
            if self._kwargs.get("ns_uri") and not value.ns_uri:
                value.ns_uri = self._kwargs["ns_uri"]
            if not value.ns_prefix and self.ns_prefix:
                value.ns_prefix = self.ns_prefix
            return value
        if isinstance(value, Mapping):
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
        elem : Element or Mapping[str, Any] or Any
            New element as Element instance
            or mapping of components' values {name: value}
            or content value of element
        """
        self.elements.append(self._check_value(elem))
        self._assigned = True

    def extend(self, iterable):
        """
        Add multiple elements

        Parameters
        ----------
        iterable : Iterable[Element or Mapping[str, Any] or Any]
            Iterable of elements as Element instances
            or mapping of components' values {name: value}
            or content value of element
        """
        for elem in iterable:
            self.append(elem)

    def add(self, value):
        """
        Add one or more elements

        Parameters
        ----------
        value : Element or Mapping[str, Any] or Iterable[Element or Mapping[str, Any]]
            New element(s) as element instance(s) or mapping(s) of components' values {name: value}
        """
        if isinstance(value, (list, tuple)):
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

    def validate(self, name=None):
        for idx, element in enumerate(self.elements):
            name_path = object_to_list(name)
            name_path.append('[{}]'.format(idx))
            element.validate(name_path)
        super(Element, self).validate(name)

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
        if name not in map(str, chain(self.base_element_cls._attrs,
                                      self.base_element_cls._children)):
            raise AttributeError("Elements of type '{}' does not have '{}' attribute or child"
                                 .format(self.base_element_cls, name))
        if not self.elements:
            raise AttributeError("Instances of '{}' have not been assigned"
                                 .format(self.base_element_cls.__name__))
        if len(self.elements) > 1:
            raise AttributeError("Cannot get attribute: more than one elements have been assigned. "
                                 "Choose element and get its' attribute.")
        return getattr(self.elements[0], name)

    def __setattr__(self, name, value):
        if (self._inited
                and name != 'base_element_cls'
                and name in map(str, chain(self.base_element_cls._attrs,
                                           self.base_element_cls._children))):
            if value is None:
                self.clear()
                return
            if len(self.elements) != 1:
                raise AttributeError("Cannot set attribute: {} elements have been assigned. "
                                     "Choose element and set its' attribute.".format(len(self.elements)))
            setattr(self.elements[0], name, value)
        else:
            super(MultipleElements, self).__setattr__(name, value)

    def __repr__(self):
        super_repr = super(MultipleElements, self).__repr__()
        if not hasattr(self, 'base_element_cls'):
            return super_repr
        s_match = re.match(r'^[^(]+\((.*?)\)$', super_repr)
        s_repr = s_match.group(1) if s_match else ''
        base_cls_repr = "base_element_cls={!r}".format(self.base_element_cls)
        return "{}({})".format(self.__class__.__name__, ", ".join(filter(None, [base_cls_repr, s_repr])))

    def get_namespaces(self, assigned_only=True, attrs_only=False):
        namespaces = super(MultipleElements, self).get_namespaces()
        for elem in self.elements:
            namespaces.update(elem.get_namespaces(assigned_only))
        return namespaces


def _build_component_getter(name):
    """
    Build attribute or child element getter

    Parameters
    ----------
    name : NSComponentName
        name of an attribute or child element
    """
    def getter(self):
        component = getattr(self, name.priv_name)
        return component.value if isinstance(component, ElementAttribute) else component
    return getter


def _build_component_setter(name):
    """
    Build attribute or child element setter

    Parameters
    ----------
    name : NSComponentName
        name of an attribute or child element
    """

    def setter(self, value):
        component = getattr(self, name.priv_name)
        if value is None:
            component.clear()
        elif isinstance(component, ElementAttribute):
            if isinstance(value, ElementAttribute):
                raise InvalidAttributeValueError(name, value)
            component.value = value
        elif isinstance(component, MultipleElements):
            component.clear()
            component.add(value)
        elif isinstance(value, component.__class__):
            if not component.compatible_with(value):
                raise InvalidElementValueError(name, component.__class__, value,
                                               msg="Value class or its attributes are incompatible.")
            setattr(self, name.priv_name, value)
            self._children[name] = value
        elif isinstance(value, Element):
            raise InvalidElementValueError(name, component.__class__, value)
        elif isinstance(value, Mapping):
            args = dict(**value)
            args.update(component.settings)
            new_value = component.__class__(**args)
            setattr(self, name.priv_name, new_value)
            self._children[name] = new_value
        elif (component.content_name
              and (not component.required_attrs
                   or len(component.required_attrs) == 1
                       and component.content_name in component.required_attrs)):
            setattr(component, component.content_name.pub_name, value)
        elif len(component.children) == 1 and not component.required_attrs:
            child_name = next(iter(component.children))
            setattr(component, str(child_name), value)
        else:
            raise InvalidElementValueError(name, component.__class__, value)
        self._assigned = value is not None

    return setter


# backward compatibility
@deprecated_class("Use ElementMeta class instead")
class ItemElementMeta(ElementMeta):
    pass

@deprecated_class("Use Element class instead")
class ItemElement(Element):
    pass
