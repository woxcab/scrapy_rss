# -*- coding: utf-8 -*-

import scrapy
from scrapy.item import BaseItem
from .elements import *
from . import meta


class RssItem(meta.item.BaseFeedItem):
    title = TitleElement()
    link = LinkElement()
    description = DescriptionElement()
    author = AuthorElement()
    category = meta.MultipleElements(CategoryElement)
    comments = CommentsElement()
    enclosure = EnclosureElement()
    guid = GuidElement()
    pubDate = PubDateElement()
    source = SourceElement()


class ExtendableItem(scrapy.Item):
    def __setattr__(self, name, value):
        if name in self.fields:
            raise AttributeError("Use item[{!r}] = {!r} to set field value".format(name, value))
        super(BaseItem, self).__setattr__(name, value)


class RssedItem(ExtendableItem):
    def __init__(self, *args, **kwargs):
        super(RssedItem, self).__init__(*args, **kwargs)
        self.rss = RssItem()

