# -*- coding: utf-8 -*-

from itertools import chain
from collections import Counter

from packaging import version
from datetime import datetime
from dateutil.tz import tzlocal
import six
import scrapy
from scrapy.exporters import XmlItemExporter

from .items import RssItem
from .utils import format_rfc822
from .exceptions import *
from . import meta


class RssItemExporter(XmlItemExporter):
    def __init__(self, file, channel_title, channel_link, channel_description,
                 namespaces=None, item_cls=None,
                 language=None, copyright=None, managing_editor=None, webmaster=None,
                 pubdate=None, last_build_date=None, category=None, generator=None,
                 docs=None, ttl=None,
                 **kwargs):
        """
        RSS parameters semantics: https://validator.w3.org/feed/docs/rss2.html

        Parameters
        ----------
        namespaces : {str or None : str} or tuple of (str or None, str) or list of (str or None, str) or None
            predefined XML namespaces {prefix: URI, ...} or [(prefix, URI), ...]
        item_cls : type
            main class of RSS items (default: RssItem)

        Item fields that corresponds to RSS element with attributes or sub-elements,
        must be a dictionary-like such as
        {"attribute-name": "attribute-value"} (with special key "content" if RSS element must have content)
        or {"sub-element-name": "sub-element-content"}

        For example, the dictionary for <guid> element:
            >>> {'isPermalink': 'False', 'content': '0123456789abcdef'}
            that converts into
            <guid isPermalink="False">0123456789abcdef</guid>
        """
        kwargs['root_element'] = 'rss'
        kwargs['item_element'] = 'item'
        super(RssItemExporter, self).__init__(file, **kwargs)

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
        self.channel_last_build_date = last_build_date if last_build_date \
            else datetime.today().replace(tzinfo=tzlocal())
        self.channel_category = ([category] if category and isinstance(category, six.string_types)
                                 and not isinstance(category, (list, set, tuple))
                                 else category)
        self.channel_generator = generator if generator is not None else 'Scrapy {}'.format(scrapy.__version__)
        self.channel_docs = docs
        self.channel_ttl = ttl

        if not item_cls:
            item_cls = RssItem
        elif not issubclass(item_cls, RssItem):
            raise ValueError('Item class must be RssItem class or its subclass')
        self._item_cls = item_cls

        if not namespaces:
            namespaces = {}
        elif isinstance(namespaces, (list, tuple)):
            namespaces = dict(namespaces)
        namespaces_iter = namespaces.items() if isinstance(namespaces, dict) else namespaces
        item_cls_namespaces = item_cls().get_namespaces(False)
        self._namespaces = {}
        skipped_ns_prefixes = set()
        for ns_prefix, ns_uri in chain(namespaces_iter, item_cls_namespaces):
            if ns_prefix in skipped_ns_prefixes:
                continue
            if ns_prefix in self._namespaces and ns_uri != self._namespaces[ns_prefix]:
                self._namespaces.pop(ns_prefix)
                skipped_ns_prefixes.add(ns_prefix)
            else:
                self._namespaces[ns_prefix] = ns_uri

    if version.parse(scrapy.__version__) < version.parse('1.4.0'):  # pragma: no cover
        def _export_xml_field(self, name, serialized_value, depth):
            return super(RssItemExporter, self)._export_xml_field(name, serialized_value)

    def start_exporting(self):
        self.xg.startDocument()
        for ns_prefix, ns_uri in self._namespaces.items():
            self.xg.startPrefixMapping(ns_prefix, ns_uri)
        root_attrs = {(None, 'version'): '2.0'}
        self.xg.startElementNS((None, self.root_element), self.root_element, root_attrs)
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

        item_namespaces = set()
        if item.__class__ is not self._item_cls:
            item_namespaces = item.get_namespaces()
            item_namespaces -= set(self._namespaces.items())
            ns_prefix_count = Counter(ns_prefix for ns_prefix, _ in item_namespaces)
            item_namespaces = {ns for ns in item_namespaces if ns_prefix_count[ns[0]] == 1}
        item_namespaces = dict(item_namespaces)

        for elem_ns_prefix, elem_ns_uri in item_namespaces.items():
            self.xg.startPrefixMapping(elem_ns_prefix, elem_ns_uri)
        self.xg.startElementNS((None, self.item_element), self.item_element, {})

        for elem_name, elem_descr in item.elements.items():
            elem_value = getattr(item, str(elem_name))
            if elem_value.assigned:
                elem_values = elem_value if isinstance(elem_value, meta.MultipleElements) else (elem_value,)
                for elem_value in elem_values:
                    if not elem_value.is_valid():
                        raise InvalidRssItemAttributesError(elem_name,
                                                            list(elem_value.required_attrs),
                                                            elem_value.content_arg)

                    attrs = elem_value.serialize()
                    content = attrs.pop(elem_descr.content_arg.xml_name, None) if elem_descr.content_arg else None
                    undeclared_elem_namespaces = {ns_prefix: ns_uri
                                                  for ns_prefix, ns_uri in elem_descr.get_namespaces()
                                                  if (ns_prefix not in self._namespaces 
                                                      or self._namespaces[ns_prefix] != ns_uri)
                                                  and (ns_prefix not in item_namespaces 
                                                       or item_namespaces[ns_prefix] != ns_uri)}
                    if elem_name.ns_prefix:
                        elem_qname = '{}:{}'.format(elem_name.ns_prefix, elem_name.name)
                    else:
                        elem_qname = elem_name.name
                    for ns_prefix, ns_uri in undeclared_elem_namespaces.items():
                        self.xg.startPrefixMapping(ns_prefix, ns_uri)
                    self.xg.startElementNS(elem_name.xml_name, elem_qname, attrs)
                    if content:
                        self.xg.characters(content)
                    self.xg.endElementNS(elem_name.xml_name, elem_qname)
                    for ns_prefix, ns_uri in undeclared_elem_namespaces.items():
                        self.xg.endPrefixMapping(ns_prefix)

        self.xg.endElementNS((None, self.item_element), self.item_element)
        for elem_ns_prefix in item_namespaces:
            self.xg.endPrefixMapping(elem_ns_prefix)

    def finish_exporting(self):
        self.xg.endElement(self.channel_element)
        self.xg.endElementNS((None, self.root_element), self.root_element)
        for ns_prefix, ns_uri in self._namespaces.items():
            self.xg.startPrefixMapping(ns_prefix, ns_uri)
        self.xg.endDocument()
