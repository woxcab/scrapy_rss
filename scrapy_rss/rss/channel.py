# -*- coding: utf-8 -*-

from .. import meta
from .channel_elements import *

class ChannelElement(meta.Element):
    """
    Attributes
    ----------
    title
        The name of the channel.
    link
        The URL to the HTML website corresponding to the channel.
    description
        Phrase or sentence describing the channel.
    language
        The language the channel is written in.

        A list of allowable values for this element, as provided by Netscape, `is here <https://www.rssboard.org/rss-language-codes>`_.

        You may also use `values defined <https://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes>`_ by the W3C.
    copyright
        Copyright notice for content in the channel.
    managingEditor
        Email address for person responsible for editorial content.
    webMaster
        Email address for person responsible for technical issues relating to channel.
    pubDate
        The publication date for the content in the channel.
    lastBuildDate
        The last time the content of the channel changed.
    category
        Specify one or more categories that the channel belongs to.
    generator
        A string indicating the program used to generate the channel.
    docs
        A URL that points to the documentation for the format used in the RSS file.
    cloud
        Allows processes to register with a cloud to be notified of updates to the channel,
        implementing a lightweight publish-subscribe protocol for RSS feeds.
    ttl
        Stands for time to live. It's a number of minutes that indicates how long a channel can be cached before refreshing from the source.
    image
        Specifies a GIF, JPEG or PNG image that can be displayed with the channel.
    rating
        The `PICS <https://www.w3.org/PICS/>`_ rating for the channel.
    textInput
        Specifies a text input box that can be displayed with the channel.
    skipHours
        A hint for aggregators telling them which hours they can skip.
        This element contains up to 24 `<hour>` sub-elements
        whose value is a number between 0 and 23, representing a time in GMT,
        when aggregators, if they support the feature, may not read the channel on hours
        listed in the `<skipHours>` element. The hour beginning at midnight is hour zero.
    skipDays
        A hint for aggregators telling them which days they can skip.
        This element contains up to seven `<day>` sub-elements
        whose value is Monday, Tuesday, Wednesday, Thursday, Friday, Saturday or Sunday.
        Aggregators may not read the channel during days listed in the `<skipDays>` element.
    """
    title = TitleElement(required=True)
    link = LinkElement(required=True)
    description = DescriptionElement(required=True)
    language = LanguageElement()
    copyright = CopyrightElement()
    managingEditor = ManagingEditorElement()
    webMaster = WebMasterElement()
    pubDate = PubDateElement()
    lastBuildDate = LastBuildDateElement()
    category = meta.MultipleElements(CategoryElement)
    generator = GeneratorElement()
    docs = DocsElement()
    cloud = CloudElement()
    ttl = TtlElement()
    image = ImageElement()
    rating = RatingElement()
    textInput = TextInputElement()
    skipHours = SkipHoursElement()
    skipDays = SkipDaysElement()


    def validate(self, name=None):
        if self.image.assigned:
            if not self.image.title.value:
                self.image.title = self.title.value
            if not self.image.link.value:
                self.image.link = self.link.value
        super(ChannelElement, self).validate(name)
