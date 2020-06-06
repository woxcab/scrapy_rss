# -*- coding: utf-8 -*-

import re
from .nscomponent import BaseNSComponent


class ItemElementAttribute(BaseNSComponent):
    def __init__(self, value=None, serializer=lambda x: str(x),
                 required=False, is_content=False, **kwargs):
        """
        Construct attribute of an element

        Parameters
        ----------
        value : Any
            Default attribute value, None means unassigned
        serializer : callable
            Function to serialize the attribute value to string for a XML document
        required : bool
             Whether the attribute is required
        is_content : bool
             Whether the "attribute" is an element content
        """
        super(ItemElementAttribute, self).__init__(**kwargs)
        if is_content and self.ns_uri:
            raise ValueError("Content cannot have namespace")
        self.__required = required
        self.__is_content = is_content
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
        return self.__required

    @property
    def is_content(self):
        """
        Returns
        -------
        bool
            Whether the attribute is an element content
        """
        return self.__is_content

    def __repr__(self):
        s_match = re.match(r'^[^(]+\((.*?)\)$', super(ItemElementAttribute, self).__repr__())
        s_repr = ", " + s_match.group(1) if s_match else ''
        return "{}(value={!r}, serializer={!r}, required={!r}, is_content={!r}{})"\
            .format(self.__class__.__name__, self.value, self.serializer,
                    self.__required, self.__is_content, s_repr)
