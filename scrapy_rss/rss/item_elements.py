# -*- coding: utf-8 -*-

from .. import meta
from ..utils import format_rfc822


class TitleElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)


class LinkElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)


class DescriptionElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)


class AuthorElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)


class CategoryElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)


class CommentsElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)


class EnclosureElement(meta.Element):
    """
    Describes a media object that is attached to the item.

    Attributes
    ----------
    url
        HTTP URL where the enclosure is located.
    length
        How big it is in bytes.
    type
        A standard MIME type.
    """
    url = meta.ElementAttribute(required=True)
    length = meta.ElementAttribute(required=True)
    type = meta.ElementAttribute(required=True)


class GuidElement(meta.Element):
    """
    Indicates when the item was published.

    Attributes
    ----------
    value
        A string that uniquely identifies the item
    isPermaLink
        A boolean. If its value is `false`, the guid may not be assumed to be a url,
        or a url to anything in particular.

        By default, it equals to `true`.
    """
    isPermaLink = meta.ElementAttribute(required=False, serializer=lambda v: str(v).lower(), value=True)
    value = meta.ElementAttribute(required=True, is_content=True)


class PubDateElement(meta.Element):
    value = meta.ElementAttribute(required=True, serializer=format_rfc822, is_content=True)


class SourceElement(meta.Element):
    url = meta.ElementAttribute(required=True)
    title = meta.ElementAttribute(is_content=True)
