# -*- coding: utf-8 -*-

import re

from ..exceptions import NoNamespaceURIError, InvalidComponentError
from ..utils import Iterable


class BaseNSComponent(object):
    _ns_prefix = ''
    _ns_uri = ''

    def __init__(self, ns_prefix=None, ns_uri=None):
        """
        Base class for elements, attributes and its names that can be namespaced

        Parameters
        ----------
        ns_prefix : str or None
            a namespace prefix
        ns_uri : str or None
            a namespace URI
        """
        self._ns_prefix = ns_prefix or ''
        self._ns_uri = ns_uri or ''
        if ns_prefix and not ns_uri:
            raise NoNamespaceURIError(self, None, "No URI for prefix '{}'".format(ns_prefix))

    @property
    def ns_prefix(self):
        """
        Get the namespace prefix

        Returns
        -------
        str or None
            The namespace prefix
        """
        return self._ns_prefix

    @ns_prefix.setter
    def ns_prefix(self, ns_prefix):
        """
        Set the namespace prefix

        Parameters
        ----------
        ns_prefix : str or None
            A new namespace prefix

        Raises
        ------
        NoNamespaceURIError
            If component does not have namespace URI
        ValueError
            If the namespace prefix is already non-empty
        """
        if self._ns_prefix == ns_prefix:
            return
        if not self._ns_uri:
            raise NoNamespaceURIError(self, None, "namespace prefix cannot be set when no namespace URI, assign URI at first")
        if self._ns_prefix:
            raise ValueError("Namespace prefix is already non-empty")
        self._ns_prefix = ns_prefix

    @property
    def ns_uri(self):
        """
        Get the namespace URI

        Returns
        -------
        str or None
            The namespace URI
        """
        return self._ns_uri

    @ns_uri.setter
    def ns_uri(self, ns_uri):
        """
        Set the namespace URI

        Parameters
        ----------
        ns_uri : str or None
            A new namespace URI

        Raises
        ------
        ValueError
            If the namespace URI is already non-empty
        """
        if self._ns_uri == ns_uri:
            return
        if self._ns_uri:
            raise ValueError("Namespace URI is already non-empty")
        self._ns_uri = ns_uri

    @property
    def settings(self):
        """
        Component settings that're defined on initialization.

        Returns
        -------
        dict[str, any]
            Dictionary of settings where keys match the constructor arguments

        """
        return {'ns_prefix': self._ns_prefix, 'ns_uri': self._ns_uri}

    def compatible_with(self, other):
        """
        Check other component compatibility for assignment to this instance

        Parameters
        ----------
        other : any

        Returns
        -------
        bool
        Whether other value is compatible with this instance for assignment

        """
        return (self.__class__ == getattr(other, '__class__', None)
                and all(getattr(other, s) == v for s, v in self.settings.items()))

    def __repr__(self):
        if not hasattr(self, '_ns_prefix') or not hasattr(self, '_ns_uri'):
            return super(BaseNSComponent, self).__repr__()
        return "{}(ns_prefix={!r}, ns_uri={!r})"\
            .format(self.__class__.__name__, self._ns_prefix, self._ns_uri)

    def get_namespaces(self):
        """
        Get namespace of the component

        Returns
        -------
        set of (str or None, str or None)
            Set of pair **(namespace_prefix, namespace_uri)** or empty set
        """
        if self._ns_uri:
            return {(self._ns_prefix, self._ns_uri)}
        return set()

    def validate(self, name=None):
        """
        Validate component.
        Component can be modified during validation.

        Parameters
        ----------
        name: str or NSComponentName or Iterable[str or NSComponentName] or None
            Name path of component

        Raises
        ------
        InvalidComponentError
            If this component is invalid
        """
        if self.ns_prefix and not self.ns_uri:
            raise NoNamespaceURIError(self, name, "no namespace URI for prefix '{}'".format(self.ns_prefix))

    def is_valid(self, name=None):
        """
        Validate component.

        Returns
        -------
        bool
            Whether this component is valid
        """
        try:
            self.validate(name)
        except InvalidComponentError:
            return False
        return True


class NSComponentName(BaseNSComponent):
    def __init__(self, name, ns_prefix=None, ns_uri=None):
        """
        Component' name wrapper

        Parameters
        ----------
        name : str
            the component name that can optionally contain a namespace prefix
            using delimiter __ (double underscores) such as nsprefix__name
        ns_prefix : str or None
            a namespace prefix
        ns_uri : str or None
            a namespace URI
        """
        if '__' in name.rstrip('_'):
            secondary_ns_prefix, name = name.split('__', 1)
        else: 
            secondary_ns_prefix = None
        super(NSComponentName, self).__init__(ns_prefix=ns_prefix or secondary_ns_prefix,
                                              ns_uri=ns_uri)
        self._name = name
        if secondary_ns_prefix:
            self._public_fullname = '{}__{}'.format(secondary_ns_prefix, name)
        else:
            self._public_fullname = name
        self._private_fullname = '__{}'.format(self._public_fullname) 

    @property
    def settings(self):
        settings = super(NSComponentName, self).settings
        settings['name'] = self._name
        return settings

    @property
    def name(self):
        """
        Get main name of the component without namespace information

        Returns
        -------
        str
            main component name
        """
        return self._name

    @property
    def xml_name(self):
        """
        Get tuple **(namespace_uri, name)** for XML handlers

        Returns
        -------
        (str or None, str)
            component name in the namespaced SAX format where the second item without trailing underscores
        """
        return self._ns_uri, self._name.rstrip('_')

    @property
    def pub_name(self):
        """
        Get component name with namespace URI in the Python public notation format
        such as **nsprefix__name** or **name** if no namespace

        Returns
        -------
        str
            public component name
        """
        return self._public_fullname

    @property
    def priv_name(self):
        """
        Get component name with namespace URI in the Python pseudo-private notation format
        such as **__nsprefix__name** or **__name** if no namespace

        Returns
        -------
        str
            private component name
        """
        return self._private_fullname

    def __str__(self):
        return self._public_fullname

    def __key(self):
        return self._ns_uri, self._name

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, NSComponentName):
            return self.__key() == other.__key()
        raise NotImplementedError("Cannot compare instances of {} and {}".format(self.__class__, other.__class__))

    def __repr__(self):
        super_repr = super(NSComponentName, self).__repr__()
        if not hasattr(self, '_name'):
            return super_repr
        s_match = re.match(r'^[^(]+\((.*?)\)$', super_repr)
        s_repr = ", " + s_match.group(1) if s_match else ''
        return "{}(name={!r}{})".format(self.__class__.__name__, self._name, s_repr)
