# -*- coding: utf-8 -*-

from itertools import chain
from collections import Counter
from operator import itemgetter

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
        item_cls_namespaces = item_cls().get_namespaces(False, attrs_only=False)
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
        self._started_ns_counter = Counter()


    if version.parse(scrapy.__version__) < version.parse('1.4.0'):
        def _export_xml_field(self, name, serialized_value, depth):
            return super(RssItemExporter, self)._export_xml_field(name, serialized_value)

    def _export_xml_element(self, element, xml_name=None, attrs_only_namespaces=True):
        """
        Export the element as an XML element

        Parameters
        ----------
        element : Element
        xml_name : (str or None, str) or None
            Name of the base XML element in the format **(ns_uri, name)**.
            If it's None then export children XML elements only without parent element
        attrs_only_namespaces : bool
            Whether extract namespaces from attributes and itself only
        """
        if not isinstance(element, meta.Element):
            raise ValueError('Argument element must be instance of <Element>, not <{!r}>'.format(element))

        if xml_name:
            namespaces = element.get_namespaces(attrs_only=attrs_only_namespaces)
            attrs_namespaces = element.get_namespaces(attrs_only=True)
            new_namespaces = namespaces - set(self._started_ns_counter)
            count_prefixes = Counter(map(itemgetter(0), new_namespaces))
            # ignore multiple namespaces with the same prefix
            new_namespaces = {ns for ns in namespaces
                              if count_prefixes[ns[0]] == 1
                              or ns in attrs_namespaces and ns not in self._started_ns_counter}
            self._started_ns_counter.update(new_namespaces)
            qname = '{}:{}'.format(element.ns_prefix, xml_name[1]) if element.ns_prefix else xml_name

            for ns_prefix, ns_uri in new_namespaces:
                self.xg.startPrefixMapping(ns_prefix, ns_uri)

        element_instances = element if isinstance(element, meta.MultipleElements) else (element,)
        for instance in element_instances:
            if not instance.is_valid():
                raise InvalidFeedItemComponentsError(instance)

            attrs = instance.serialize_attrs()
            content = attrs.pop(instance.content_name.xml_name, None) if instance.content_name else None
            if xml_name:
                self.xg.startElementNS(xml_name, qname, attrs)
            if content:
                self.xg.characters(content)
            for child_name, child in instance.children.items():
                if child.assigned:
                    self._export_xml_element(child, child_name.xml_name)
            if xml_name:
                self.xg.endElementNS(xml_name, qname)

        if xml_name:
            for ns_prefix, ns_uri in new_namespaces:
                self.xg.endPrefixMapping(ns_prefix)
            self._started_ns_counter -= Counter(new_namespaces)


    def start_exporting(self):
        self.xg.startDocument()

        for ns_prefix, ns_uri in self._namespaces.items():
            self.xg.startPrefixMapping(ns_prefix, ns_uri)
        self._started_ns_counter.update(self._namespaces.items())

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
            raise InvalidFeedItemError("Item must have 'rss' field of type 'RssItem'")
        if not isinstance(item, RssItem):
            item = item.rss

        self._export_xml_element(item, (None, self.item_element), attrs_only_namespaces=False)


    def finish_exporting(self):
        self.xg.endElement(self.channel_element)
        self.xg.endElementNS((None, self.root_element), self.root_element)
        for ns_prefix, ns_uri in self._namespaces.items():
            self.xg.endPrefixMapping(ns_prefix)
        self._started_ns_counter -= Counter(self._namespaces.items())
        self.xg.endDocument()
