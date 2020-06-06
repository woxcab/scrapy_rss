# -*- coding: utf-8 -*-

import re

from ..exceptions import NoNamespaceURIError


class BaseNSComponent(object):
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
        if ns_prefix and not ns_uri:
            raise NoNamespaceURIError("No URI for prefix '{}'".format(ns_prefix))
        self._ns_prefix = ns_prefix or ''
        self._ns_uri = ns_uri or ''

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
            raise NoNamespaceURIError("Namespace prefix cannot be set when no namespace URI")
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

    def __repr__(self):
        return "{}(ns_prefix={!r}, ns_uri={!r})"\
            .format(self.__class__.__name__, self._ns_prefix, self._ns_uri)

    def get_namespaces(self, assigned_only=True):
        """
        Get all namespaces of the component and its children

        Parameters
        ----------
        assigned_only : bool
            whether return namespaces of assigned children only

        Returns
        -------
        set of (str or None, str or None)
            Set of pairs (namespace_prefix, namespace_uri)
        """
        if self._ns_uri:
            return {(self._ns_prefix, self._ns_uri)}
        return set()


class NSComponentName(BaseNSComponent):
    def __init__(self, name, ns_prefix=None, ns_uri=None):
        """
        Component' name wrapper

        Parameters
        ----------
        name : str
            the component name that can optionally contain a namespace prefix
            using delimiter __ (double underscores) such as ns__name
        ns_prefix : str or None
            a namespace prefix
        ns_uri : str or None
            a namespace URI
        """
        if '__' in name:
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
            component name in the namespaced SAX format
        """
        return self._ns_uri, self._name

    @property
    def pub_name(self):
        """
        Get component name with namespace URI in the Python public notation format
        such as **uri__name** or **name** if no namespace

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
        such as **__uri__name** or **__name** if no namespace

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
        s_match = re.match(r'^[^(]+\((.*?)\)$', super(NSComponentName, self).__repr__())
        s_repr = ", " + s_match.group(1) if s_match else ''
        return "{}(name={!r}{})".format(self.__class__.__name__, self._name, s_repr)
