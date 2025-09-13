# -*- coding: utf-8 -*-

from itertools import chain
from collections import Counter
from operator import itemgetter

from datetime import datetime
import scrapy
from scrapy.exporters import XmlItemExporter

from .items import RssItem, FeedItem
from .rss.channel import ChannelElement
from .rss.old.items import RssItem as OldRssItem
from .exceptions import *
from .utils import get_tzlocal, is_strict_subclass, get_full_class_name, deprecated_class
from . import meta


class FeedItemExporter(XmlItemExporter):
    def __init__(self, file, channel_title, channel_link, channel_description,
                 namespaces=None, item_cls=None,
                 language=None, copyright=None, managing_editor=None, webmaster=None,
                 pubdate=None, last_build_date=None, category=None,
                 generator='Scrapy {}'.format(scrapy.__version__),
                 docs=None, cloud=None, ttl=None, image=None, rating=None, text_input=None,
                 skip_hours=None, skip_days=None,
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
        {"attribute-name": "attribute-value"} or {"sub-element-name": "sub-element-content"}
        or any value if corresponding sub-element contains single attribute marked as content

        For example, the dictionary for <guid> element:
            >>> {'isPermalink': 'False', 'content': '0123456789abcdef'}
            that converts into
            <guid isPermalink="False">0123456789abcdef</guid>
        """
        kwargs['root_element'] = 'rss'
        kwargs['item_element'] = 'item'
        super(FeedItemExporter, self).__init__(file, **kwargs)

        self.channel_element_name = 'channel'
        self.channel = ChannelElement()

        self.channel.title = channel_title
        self.channel.link = channel_link
        self.channel.description = channel_description

        self.channel.language = language
        self.channel.copyright = copyright
        self.channel.managingEditor = managing_editor
        self.channel.webMaster = webmaster
        self.channel.pubDate = pubdate
        self.channel.lastBuildDate = last_build_date if last_build_date else datetime.now(get_tzlocal())
        self.channel.category = category
        self.channel.generator = generator
        self.channel.docs = docs
        self.channel.cloud = cloud
        self.channel.ttl = ttl
        self.channel.image = image
        self.channel.rating = rating
        self.channel.textInput = text_input
        self.channel.skipHours = skip_hours
        self.channel.skipDays = skip_days

        if not item_cls:
            item_cls = RssItem
        elif not is_strict_subclass(item_cls, FeedItem):
            raise ValueError('Item class must be strict subclass of FeedItem')
        self._item_cls = item_cls
        self._allowed_item_classes = tuple({RssItem, OldRssItem, self._item_cls})

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
            raise ValueError('Argument element must be instance of <Element>, not <{}>'
                             .format(element.__class__.__name__ if hasattr(element, '__class__')
                                     else repr(element)))

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
            try:
                instance.validate(xml_name[1] if xml_name else None)
            except InvalidComponentError as e:
                raise InvalidFeedItemComponentsError(instance, msg=str(e))

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
        self.xg.startElement(self.channel_element_name, {})
        self._export_xml_element(self.channel)

    def export_item(self, item):
        if (not isinstance(item, self._allowed_item_classes)
                and not isinstance(getattr(item, 'rss', None), RssItem)):
            raise InvalidFeedItemError("Item must be type {} or have 'rss' field of type 'RssItem'"
                                       .format(', '.join(map(repr, map(get_full_class_name, self._allowed_item_classes)))))
        if not isinstance(item, self._allowed_item_classes):
            item = item.rss

        self._export_xml_element(item, (None, self.item_element), attrs_only_namespaces=False)


    def finish_exporting(self):
        self.xg.endElement(self.channel_element_name)
        self.xg.endElementNS((None, self.root_element), self.root_element)
        for ns_prefix, ns_uri in self._namespaces.items():
            self.xg.endPrefixMapping(ns_prefix)
        self._started_ns_counter -= Counter(self._namespaces.items())
        self.xg.endDocument()


@deprecated_class('Use FeedItemExporter instead')
class RssItemExporter(FeedItemExporter):
    pass
