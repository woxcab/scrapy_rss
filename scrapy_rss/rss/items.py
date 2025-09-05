from .item_elements import *
from ..meta.item import FeedItem


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

    def is_valid(self):
        return (self.title.assigned or self.description.assigned) and super(RssItem, self).is_valid()


class RssedItem(FeedItem):
    def __init__(self, *args, **kwargs):
        super(RssedItem, self).__init__(*args, **kwargs)
        self.rss = RssItem()
