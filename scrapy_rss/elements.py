# -*- coding: utf-8 -*-

import scrapy_rss.meta as meta
from scrapy_rss.utlis import format_rfc822


class TitleElement(meta.ItemElement):
    title = meta.ItemElementAttribute(required=True, is_content=True)


class LinkElement(meta.ItemElement):
    link = meta.ItemElementAttribute(required=True, is_content=True)


class DescriptionElement(meta.ItemElement):
    description = meta.ItemElementAttribute(required=True, is_content=True)


class AuthorElement(meta.ItemElement):
    author = meta.ItemElementAttribute(required=True, is_content=True)


class CategoryElement(meta.ItemElement):
    category = meta.ItemElementAttribute(required=True, is_content=True)


class CommentsElement(meta.ItemElement):
    comments = meta.ItemElementAttribute(required=True, is_content=True)


class EnclosureElement(meta.ItemElement):
    url = meta.ItemElementAttribute(required=True)
    length = meta.ItemElementAttribute(required=True)
    type = meta.ItemElementAttribute(required=True)


class GuidElement(meta.ItemElement):
    isPermaLink = meta.ItemElementAttribute(required=False, serializer=lambda v: str(v).lower(), value=False)
    guid = meta.ItemElementAttribute(required=True, is_content=True)


class PubDateElement(meta.ItemElement):
    datetime = meta.ItemElementAttribute(required=True, serializer=format_rfc822, is_content=True)


class SourceElement(meta.ItemElement):
    url = meta.ItemElementAttribute(required=True)

