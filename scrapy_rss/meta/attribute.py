# -*- coding: utf-8 -*-

import re

from .nscomponent import BaseNSComponent
from ..exceptions import InvalidComponentError
from ..utils import deprecated_class


class ElementAttribute(BaseNSComponent):
    def __init__(self, value=None, serializer=str,
                 required=False, is_content=False, **kwargs):
        """
        Construct attribute of an element

        Parameters
        ----------
        value : Any
            Default attribute value, None means unassigned
        serializer : callable
            Function to serialize the attribute value to string for an XML document
        required : bool
             Whether the attribute is required
        is_content : bool
             Whether the "attribute" is an element content
        """
        super(ElementAttribute, self).__init__(**kwargs)
        if is_content and self.ns_uri:
            raise ValueError("Content cannot have namespace")
        self._required = required
        self._is_content = is_content
        self.serializer = serializer
        self.value = value

    @property
    def required(self):
        """
        Returns
        -------
        bool
            Whether the attribute is required
        """
        return self._required

    @property
    def is_content(self):
        """
        Returns
        -------
        bool
            Whether the attribute is an element content
        """
        return self._is_content

    @property
    def assigned(self):
        return self.value is not None

    @property
    def settings(self):
        settings = super(ElementAttribute, self).settings
        settings['required'] = self._required
        settings['is_content'] = self._is_content
        settings['serializer'] = self.serializer
        return settings

    def clear(self):
        self.value = None

    def get_namespaces(self, assigned_only=True):
        """
        Get namespaces of the attribute

        Parameters
        ----------
        assigned_only : bool
            whether return namespace only if the attribute is assigned

        Returns
        -------
        set of (str or None, str or None)
            Set of pairs **(namespace_prefix, namespace_uri)**
        """
        if not assigned_only or self.assigned:
            return super(ElementAttribute, self).get_namespaces()
        return set()

    def __repr__(self):
        super_repr = super(ElementAttribute, self).__repr__()
        if (not hasattr(self, 'value') or not hasattr(self, 'serializer')
                or not hasattr(self, '_required') or not hasattr(self, '_is_content')):
            return super_repr
        s_match = re.match(r'^[^(]+\((.*?)\)$', super_repr)
        s_repr = ", " + s_match.group(1) if s_match else ''
        return "{}(value={!r}, serializer={!r}, required={!r}, is_content={!r}{})"\
            .format(self.__class__.__name__, self.value, self.serializer,
                    self._required, self._is_content, s_repr)

    def validate(self, name=None):
        super(ElementAttribute, self).validate(name)
        if self.required and not self.assigned:
            raise InvalidComponentError(self, name, "required value is not assigned")


# backward compatibility
@deprecated_class("Use ElementAttribute class instead")
class ItemElementAttribute(ElementAttribute):
    pass
