# -*- coding: utf-8 -*-

import scrapy
from scrapy.item import BaseItem
from scrapy_rss.elements import *
from scrapy_rss import meta
import six


@six.add_metaclass(meta.ItemMeta)
class RssItem:
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
    def __init__(self, **kwargs):
        super(RssedItem, self).__init__(**kwargs)
        self.rss = RssItem()

