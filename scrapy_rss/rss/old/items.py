# -*- coding: utf-8 -*-

from .item_elements import *
from ...meta.item import FeedItem
from ...exceptions import InvalidComponentError
from ...utils import object_to_list


class RssItem(FeedItem):
    """
    title
        The title of the item.
    link
        The URL of the item.
    description
        The item synopsis.
    author
        Email address of the author of the item.
    category
        Includes the item in one or more categories.
    comments
        URL of a page for comments relating to the item.
    enclosure
        Describes a media object that is attached to the item.
    guid
        A string that uniquely identifies the item.
    pubDate
        Indicates when the item was published.
    source
        The RSS channel that the item came from.
    """
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

    def validate(self, name=None):
        if not self.title.assigned and not self.description.assigned:
            name_path = object_to_list(name)
            name_path.append('title')
            raise InvalidComponentError(self,
                                        name_path,
                                        "at least one of title or description must be present")
        super(RssItem, self).validate(name)


class RssedItem(FeedItem):
    def __init__(self, *args, **kwargs):
        super(RssedItem, self).__init__(*args, **kwargs)
        self.rss = RssItem()
