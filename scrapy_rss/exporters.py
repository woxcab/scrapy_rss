# -*- coding: utf-8 -*-

from distutils.version import LooseVersion

from datetime import datetime
from dateutil.tz import tzlocal
import six
import scrapy
from scrapy.exporters import XmlItemExporter
from scrapy_rss.items import RssItem
from scrapy_rss.utlis import format_rfc822
from scrapy_rss.exceptions import *
from scrapy_rss import meta


class RssItemExporter(XmlItemExporter):
    """
    Parameters semantics: https://validator.w3.org/feed/docs/rss2.html

    Item fields that corresponds to RSS element with attributes or sub-elements,
    must be a dictionary-like such as
    {"attribute-name": "attribute-value"} (with special key "content" if RSS element must have content)
    or {"sub-element-name": "sub-element-content"}

    Examples:
        * The dictionary for the ``<image>`` element:
            >>> {'url': 'http://example.com/image.png', 'title': 'Some title', 'link': 'http://example.com/'}

            that converts into

            <image>
                 <url>http://example.com/image.png</url>
                 <title>Some title</title>
                 <link>http://example.com/</link>
            </image>

        * The dictionary for <guid> element:
            >>> {'isPermalink': 'False', 'content': '0123456789abcdef'}
            that converts into
            <guid isPermalink="False">0123456789abcdef</guid>

    """

    def __init__(self, file, channel_title, channel_link, channel_description,
                 language=None, copyright=None, managing_editor=None, webmaster=None,
                 pubdate=None, last_build_date=None, category=None, generator=None,
                 docs=None, ttl=None,
                 *args, **kwargs):
        kwargs['root_element'] = 'rss'
        kwargs['item_element'] = 'item'
        super(RssItemExporter, self).__init__(file, *args, **kwargs)

        self.channel_element = 'channel'

        self.channel_title = channel_title
        self.channel_link = channel_link
        self.channel_description = channel_description

        self.channel_language = language
        self.channel_copyright = copyright
        if managing_editor and '@' not in managing_editor:
            raise ValueError('managing_editor field must contain at least e-mail. Passed: {}'.format(managing_editor))
        self.channel_managing_editor = managing_editor
        if webmaster and '@' not in webmaster:
            raise ValueError('webmaster field must contain at least e-mail. Passed: {}'.format(webmaster))
        self.channel_webmaster = webmaster
        self.channel_pubdate = pubdate
        self.channel_last_build_date = last_build_date if last_build_date else datetime.today().replace(tzinfo=tzlocal())
        self.channel_category = ([category] if category and isinstance(category, six.string_types)
                                 and not isinstance(category, (list, set, tuple))
                                 else category)
        self.channel_generator = generator if generator is not None else 'Scrapy {}'.format(scrapy.__version__)
        self.channel_docs = docs
        self.channel_ttl = ttl

    if LooseVersion(scrapy.__version__) < LooseVersion('1.4.0'):  # pragma: no cover
        def _export_xml_field(self, name, serialized_value, depth):
            return super(RssItemExporter, self)._export_xml_field(name, serialized_value)

    def start_exporting(self):
        self.xg.startDocument()
        self.xg.startElement(self.root_element, {'version': '2.0'})
        self.xg.startElement(self.channel_element, {})

        self._export_xml_field('title', self.channel_title, 1)
        self._export_xml_field('link', self.channel_link, 1)
        self._export_xml_field('description', self.channel_description, 1)
        if self.channel_language:
            self._export_xml_field('language', self.channel_language, 1)
        if self.channel_copyright:
            self._export_xml_field('copyright', self.channel_copyright, 1)
        if self.channel_managing_editor:
            self._export_xml_field('managingEditor', self.channel_managing_editor, 1)
        if self.channel_webmaster:
            self._export_xml_field('webMaster', self.channel_webmaster, 1)
        if self.channel_pubdate:
            self._export_xml_field('pubdate',
                                   format_rfc822(self.channel_pubdate)
                                   if isinstance(self.channel_pubdate, datetime)
                                   else self.channel_pubdate, 1)
        self._export_xml_field('lastBuildDate',
                               format_rfc822(self.channel_last_build_date)
                               if isinstance(self.channel_last_build_date, datetime)
                               else self.channel_last_build_date, 1)
        if self.channel_category:
            for category in self.channel_category:
                self._export_xml_field('category', category, 1)
        if self.channel_generator:
            self._export_xml_field('generator', self.channel_generator, 1)
        if self.channel_docs:
            self._export_xml_field('docs', self.channel_docs, 1)
        if self.channel_ttl:
            self._export_xml_field('ttl', self.channel_ttl, 1)

    def export_item(self, item):
        if not isinstance(item, RssItem) and not isinstance(getattr(item, 'rss', None), RssItem):
            raise InvalidRssItemError("Item must have 'rss' field of type 'RssItem'")
        if not isinstance(item, RssItem):
            item = item.rss
        self.xg.startElement(self.item_element, {})
        for elem_name, elem_descr in item.elements.items():
            elem_value = getattr(item, elem_name)
            if elem_value.assigned:
                elem_values = elem_value if isinstance(elem_value, meta.MultipleElements) else (elem_value,)
                for elem_value in elem_values:
                    if not elem_value.is_valid():
                        raise InvalidRssItemAttributesError(elem_name,
                                                            list(elem_value.required_attrs),
                                                            elem_value.content_arg)
                    attrs = elem_value.serialize()
                    content = attrs.pop(elem_descr.content_arg, None)
                    self.xg.startElement(elem_name, attrs)
                    if content:
                        self._xg_characters(content)
                    self.xg.endElement(elem_name)
        self.xg.endElement(self.item_element)

    def finish_exporting(self):
        self.xg.endElement(self.channel_element)
        self.xg.endElement(self.root_element)
        self.xg.endDocument()
