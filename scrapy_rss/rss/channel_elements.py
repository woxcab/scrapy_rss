# -*- coding: utf-8 -*-
from .. import meta
from ..utils import format_rfc822, object_to_list
from ..exceptions import InvalidComponentError


class TitleElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class LinkElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class DescriptionElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class LanguageElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class CopyrightElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class ManagingEditorElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

    def validate(self, name=None):
        if self.assigned and '@' not in self.value:
            name_path = object_to_list(name)
            name_path.append('managingEditor')
            raise InvalidComponentError(
                self,
                name_path,
                'field must contain at least e-mail, but assigned: {!r}'.format(self.value)
            )
        super(ManagingEditorElement, self).validate(name)

class WebMasterElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

    def validate(self, name=None):
        if self.assigned and '@' not in self.value:
            name_path = object_to_list(name)
            name_path.append('webMaster')
            raise InvalidComponentError(
                self,
                name_path,
                'field must contain at least e-mail, but assigned: {!r}'.format(self.value)
            )
        super(WebMasterElement, self).validate(name)

class PubDateElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True, serializer=format_rfc822)

class LastBuildDateElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True, serializer=format_rfc822)

class CategoryElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class GeneratorElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class DocsElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

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
    value = meta.ElementAttribute(required=True, is_content=True)


class ImageUrlElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class ImageTitleElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class ImageLinkElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class ImageWidthElement(meta.Element):
    value = meta.ElementAttribute(is_content=True)

class ImageHeightElement(meta.Element):
    value = meta.ElementAttribute(is_content=True)

class ImageDescriptionElement(meta.Element):
    value = meta.ElementAttribute(is_content=True)

class ImageElement(meta.Element):
    """
    Specifies a GIF, JPEG or PNG image that can be displayed with the channel.

    Attributes
    ----------
    url
        The URL of a GIF, JPEG or PNG image that represents the channel.
    title
        Describes the image, it's used in the ALT attribute of the HTML <img> tag
        when the channel is rendered in HTML.

        By default, it equals to channel title.
    link
        The URL of the site, when the channel is rendered, the image is a link to the site.

        By default, it equals to channel link.
    width
        The width of the image in pixels. Maximum value for width is 144, default value is 88.
    height
        The height of the image in pixels. Maximum value for height is 400, default value is 31.
    description
        Contains text that is included in the TITLE attribute of the link
        formed around the image in the HTML rendering.
    """
    url = ImageUrlElement(required=True)
    title = ImageTitleElement(required=True)
    link = ImageLinkElement(required=True)
    width = ImageWidthElement()
    height = ImageHeightElement()
    description = ImageDescriptionElement()


class RatingElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)


class TextInputTitleElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class TextInputDescriptionElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class TextInputNameElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class TextInputLinkElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class TextInputElement(meta.Element):
    """
    Specifies a text input box that can be displayed with the channel.

    Attributes
    ----------
    title
        The label of the Submit button in the text input area.
    description
        Explains the text input area.
    name
        The name of the text object in the text input area.
    link
        The URL of the CGI script that processes text input requests.
    """
    title = TextInputTitleElement(required=True)
    description = TextInputDescriptionElement(required=True)
    name = TextInputNameElement(required=True)
    link = TextInputLinkElement(required=True)


class SkipHoursHourElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class SkipHoursElement(meta.Element):
    hour = meta.MultipleElements(SkipHoursHourElement)


class SkipDaysDayElement(meta.Element):
    value = meta.ElementAttribute(required=True, is_content=True)

class SkipDaysElement(meta.Element):
    day = meta.MultipleElements(SkipDaysDayElement)
