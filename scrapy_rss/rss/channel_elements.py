# -*- coding: utf-8 -*-

from .. import meta
from ..utils import format_rfc822


class TitleElement(meta.Element):
    title = meta.ElementAttribute(required=True, is_content=True)

class LinkElement(meta.Element):
    link = meta.ElementAttribute(required=True, is_content=True)

class DescriptionElement(meta.Element):
    description = meta.ElementAttribute(required=True, is_content=True)

class LanguageElement(meta.Element):
    language = meta.ElementAttribute(required=True, is_content=True)

class CopyrightElement(meta.Element):
    copyright = meta.ElementAttribute(required=True, is_content=True)

class ManagingEditorElement(meta.Element):
    managingEditor = meta.ElementAttribute(required=True, is_content=True)

class WebMasterElement(meta.Element):
    webMaster = meta.ElementAttribute(required=True, is_content=True)

class PubDateElement(meta.Element):
    pubDate = meta.ElementAttribute(required=True, is_content=True, serializer=format_rfc822)

class LastBuildDateElement(meta.Element):
    lastBuildDate = meta.ElementAttribute(required=True, is_content=True, serializer=format_rfc822)

class CategoryElement(meta.Element):
    category = meta.ElementAttribute(required=True, is_content=True)

class GeneratorElement(meta.Element):
    generator = meta.ElementAttribute(required=True, is_content=True)

class DocsElement(meta.Element):
    docs = meta.ElementAttribute(required=True, is_content=True)

class CloudElement(meta.Element):
    """
    Allows processes to register with a cloud to be notified of updates to the channel, implementing a lightweight publish-subscribe protocol for RSS feeds

    Attributes
    ----------
    domain : str
        String domain name only without protocol
    port : int
        Integer port
    path : str
        The string URL path
    registerProcedure : str
        The name of the procedure to call on the cloud
    protocol : {'xml-rpc', 'http-post', 'soap'}
        The protocol of the cloud.  Acceptable values ``xml-rpc``, ``http-post`` or ``soap``
    """
    domain = meta.ElementAttribute(required=True)
    port = meta.ElementAttribute(required=True)
    path = meta.ElementAttribute(required=True)
    registerProcedure = meta.ElementAttribute(required=True)
    protocol = meta.ElementAttribute(required=True)

class TtlElement(meta.Element):
    ttl = meta.ElementAttribute(required=True, is_content=True)


class ImageUrlElement(meta.Element):
    url = meta.ElementAttribute(required=True, is_content=True)

class ImageTitleElement(meta.Element):
    title = meta.ElementAttribute(required=True, is_content=True)

class ImageLinkElement(meta.Element):
    link = meta.ElementAttribute(required=True, is_content=True)

class ImageWidthElement(meta.Element):
    width = meta.ElementAttribute(is_content=True)

class ImageHeightElement(meta.Element):
    height = meta.ElementAttribute(is_content=True)

class ImageDescriptionElement(meta.Element):
    description = meta.ElementAttribute(is_content=True)

class ImageElement(meta.Element):
    url = ImageUrlElement(required=True)
    title = ImageTitleElement(required=True)
    link = ImageLinkElement(required=True)
    width = ImageWidthElement()
    height = ImageHeightElement()
    description = ImageDescriptionElement()


class RatingElement(meta.Element):
    rating = meta.ElementAttribute(required=True, is_content=True)


class TextInputTitleElement(meta.Element):
    title = meta.ElementAttribute(required=True, is_content=True)

class TextInputDescriptionElement(meta.Element):
    description = meta.ElementAttribute(required=True, is_content=True)

class TextInputNameElement(meta.Element):
    name = meta.ElementAttribute(required=True, is_content=True)

class TextInputLinkElement(meta.Element):
    link = meta.ElementAttribute(required=True, is_content=True)

class TextInputElement(meta.Element):
    title = TextInputTitleElement(required=True)
    description = TextInputDescriptionElement(required=True)
    name = TextInputNameElement(required=True)
    link = TextInputLinkElement(required=True)


class SkipHoursHourElement(meta.Element):
    hour = meta.ElementAttribute(required=True, is_content=True)

class SkipHoursElement(meta.Element):
    hour = meta.MultipleElements(SkipHoursHourElement)


class SkipDaysDayElement(meta.Element):
    day = meta.ElementAttribute(required=True, is_content=True)

class SkipDaysElement(meta.Element):
    day = meta.MultipleElements(SkipDaysDayElement)
