# -*- coding: utf-8 -*-

from .rss.item_elements import *
from . import meta
from .meta.item import FeedItem

# Backward compatibility
from .meta.item import ExtendableItem


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

    def is_valid(self):
        return (self.title.assigned or self.description.assigned) and super(RssItem, self).is_valid()


class RssedItem(FeedItem):
    def __init__(self, *args, **kwargs):
        super(RssedItem, self).__init__(*args, **kwargs)
        self.rss = RssItem()

