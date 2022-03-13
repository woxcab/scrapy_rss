# -*- coding: utf-8 -*-

from .elements import *
from . import meta
from .meta.item import FeedItem, ExtendableItem


class RssItem(FeedItem):
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


class RssedItem(FeedItem):
    def __init__(self, *args, **kwargs):
        super(RssedItem, self).__init__(*args, **kwargs)
        self.rss = RssItem()

