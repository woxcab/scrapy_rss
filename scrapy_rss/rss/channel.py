# -*- coding: utf-8 -*-

from .. import meta
from .channel_elements import *

class ChannelElement(meta.Element):
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




















