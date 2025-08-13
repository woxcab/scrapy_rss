# -*- coding: utf-8 -*-

from .. import meta
from ..utils import format_rfc822


class TitleElement(meta.Element):
    title = meta.ElementAttribute(required=True, is_content=True)


class LinkElement(meta.Element):
    link = meta.ElementAttribute(required=True, is_content=True)


class DescriptionElement(meta.Element):
    description = meta.ElementAttribute(required=True, is_content=True)


class AuthorElement(meta.Element):
    author = meta.ElementAttribute(required=True, is_content=True)


class CategoryElement(meta.Element):
    category = meta.ElementAttribute(required=True, is_content=True)


class CommentsElement(meta.Element):
    comments = meta.ElementAttribute(required=True, is_content=True)


class EnclosureElement(meta.Element):
    url = meta.ElementAttribute(required=True)
    length = meta.ElementAttribute(required=True)
    type = meta.ElementAttribute(required=True)


class GuidElement(meta.Element):
    isPermaLink = meta.ElementAttribute(required=False, serializer=lambda v: str(v).lower(), value=False)
    guid = meta.ElementAttribute(required=True, is_content=True)


class PubDateElement(meta.Element):
    datetime = meta.ElementAttribute(required=True, serializer=format_rfc822, is_content=True)


class SourceElement(meta.Element):
    url = meta.ElementAttribute(required=True)
