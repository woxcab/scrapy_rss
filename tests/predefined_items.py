# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy_rss.meta import Element, ElementAttribute
from scrapy_rss import RssItem


class NSElement0(Element):
    attr01 = ElementAttribute(ns_prefix="prefix01", ns_uri="id01")


class NSElement1(Element):
    prefix11__attr11 = ElementAttribute(ns_uri="id11")
    prefix12__attr12 = ElementAttribute(ns_prefix="prefix12", ns_uri="id12")


class NSElement2(Element):
    attr21 = ElementAttribute(is_content=True)
    pseudo_prefix22__attr22 = ElementAttribute(ns_prefix="prefix22", ns_uri="id22")


class NSElement3(Element):
    attr31 = ElementAttribute(is_content=True)
    attr32 = ElementAttribute(ns_prefix="prefixa", ns_uri="id32")


class NSElement4(Element):
    attr41 = ElementAttribute()
    prefix42__attr41 = ElementAttribute(ns_uri="id42")


class NSItem0(RssItem):
    elem0 = Element()
    elem1 = NSElement0(ns_prefix="el_prefix1", ns_uri="el_id1")
    el_prefix2__elem2 = NSElement1(ns_uri="el_id2")
    el_prefix3__elem3 = NSElement2(ns_prefix="el_prefix3", ns_uri="el_id3")
    el_pseudo_prefix4__elem4 = NSElement0(ns_prefix="el_prefix4", ns_uri="el_id4")


class NSItem1(RssItem):
    elem1 = NSElement0(ns_prefix="el_prefix1", ns_uri="el_id1")
    el_prefix__elem2 = NSElement1(ns_uri="el_id2")
    elem3 = NSElement2(ns_prefix="el_prefix", ns_uri="el_id3")
    el_pseudo_prefix4__elem4 = NSElement0(ns_prefix="el_prefix4", ns_uri="el_id4")


class NSItem2(RssItem):
    elem1 = NSElement3(ns_prefix="prefix", ns_uri="el_id1")
    prefix__elem2 = NSElement3(ns_uri="el_id2")
    elem3 = NSElement3(ns_prefix="prefix", ns_uri="el_id3")
    el_pseudo_prefix4__elem4 = NSElement3(ns_prefix="prefix", ns_uri="el_id4")


class NSItem3(RssItem):
    elem1 = NSElement3(ns_uri="el_id1")
    elem2 = NSElement3(ns_uri="el_id2")
    elem3 = NSElement3(ns_prefix="prefix", ns_uri="el_id3")
    el_pseudo_prefix4__elem3 = NSElement3(ns_prefix="prefix2", ns_uri="el_id4")
    elem4 = NSElement4()
    elem5 = NSElement4()


class NSItem4(NSItem1):
    attr1 = ElementAttribute(ns_prefix="attr_prefix", ns_uri="attr_id1", required=True)
    attr2 = ElementAttribute(ns_prefix="el_prefix", ns_uri="attr_id2", required=True)


class NSItemNested0(RssItem):
    elem = NSItem0()


class NSItemNested1(RssItem):
    elem = NSItem1(ns_prefix="el_prefix", ns_uri="el_id")


class NSItemNested2(RssItem):
    el_prefix__elem = NSItem2(ns_uri="el_id")


class NSItemNested3(RssItem):
    el_pseudo_prefix__elem = NSItem3(ns_prefix="el_prefix", ns_uri="el_id")


class NSItemFullNested(RssItem):
    elem0 = NSItem0()
    elem1 = NSItem1(ns_prefix="el_prefix1", ns_uri="el_id1")
    el_prefix2__elem2 = NSItem2(ns_uri="el_id2")
    elem3 = NSItem3(ns_uri="el_id2")


UnicodeElement0 = type("UnicodeElement0", (Element,), {
    'název_atributu1': ElementAttribute(ns_prefix='předpona1', ns_uri='id01', required=True),
    'předpona2__název_atributu2': ElementAttribute(ns_uri='id02', required=True),
    'název_prvek3': ElementAttribute(required=True, is_content=True),
})
UnicodeElement1 = type("UnicodeElement1", (Element,), {
    'ё_имя_атр1': ElementAttribute(ns_prefix='префикс1', ns_uri='id11', required=True),
    'имя_атр2': ElementAttribute(required=True, is_content=True),
    'имя_атр3': ElementAttribute(required=True),
})
UnicodeItem = type("UnicodeItem", (RssItem,), {
    'název_elementu1': UnicodeElement0(required=True, ns_prefix='префиксё', ns_uri='id1'),
    'имя_элем2': UnicodeElement1(required=True, ns_prefix='předpona', ns_uri='id2'),
})


class PredefinedItems(object):
    def __init__(self, *args, **kwargs):
        minimal_item = RssItem()
        minimal_item.title = 'Title of minimal item'

        minimal_item2 = RssItem()
        minimal_item2.description = 'Description of minimal item'

        minimal_item3 = RssItem()
        minimal_item3.title.value = 'Directly defined title of minimal item'

        minimal_item4 = RssItem()
        minimal_item4.description.value = 'Directly defined description of minimal item'

        simple_item = RssItem()
        simple_item.title = 'Title of simple item'
        simple_item.description = 'Description of simple item'

        item_with_single_category = RssItem()
        item_with_single_category.title = 'Title of item with single category'
        item_with_single_category.category = 'Category 1'

        item_with_multiple_categories = RssItem()
        item_with_multiple_categories.title = 'Title of item with multiple categories'
        item_with_multiple_categories.category = ['Category 1', 'Category 2']

        item_with_guid = RssItem()
        item_with_guid.title = 'Title of item with guid'
        item_with_guid.guid = 'Identifier'

        item_with_unicode = RssItem()
        item_with_unicode.title = 'Title of item with unicode and special characters'
        item_with_unicode.description = "[Testing «ταБЬℓσ»: 1<2 & 4+1>3, now 20% off!]"

        item_with_enclosure = RssItem()
        item_with_enclosure.title = 'Title of item with enclosure'
        item_with_enclosure.enclosure.url = 'http://example.com/content'
        item_with_enclosure.enclosure.length = 0
        item_with_enclosure.enclosure.type = 'text/plain'

        full_rss_item = RssItem()
        full_rss_item.title = 'Title of full item'
        full_rss_item.link = 'http://example.com/item'
        full_rss_item.description = 'Item description'
        full_rss_item.author = 'Item author without the at sign'
        full_rss_item.category = ['Category 1', 'Category 2']
        full_rss_item.comments = 'http://example.com/item#comments'
        full_rss_item.enclosure = {'url': 'http://example.com/content', 'length': 0, 'type': 'text/plain'}
        full_rss_item.pubDate = datetime(2000, 1, 1, 0, 50, 15)
        full_rss_item.guid = {'isPermaLink': False, 'value': 'Identifier'}
        full_rss_item.source.url = 'https://another.example.com/feed'
        full_rss_item.source.title = 'Another feed title'

        unicode_item = UnicodeItem()
        unicode_item.title = 'Заголовок. Název položky'
        setattr(unicode_item, 'název_elementu1', {
            'název_atributu1': 'význam 1',
            'předpona2__název_atributu2': 'význam 2',
            'název_prvek3': 157
        })
        setattr(unicode_item, 'имя_элем2', {
            'ё_имя_атр1': 'Ёжик',
            'имя_атр2': 'Лиса и ёжик',
            'имя_атр3': 0
        })

        nested_item0 = NSItemNested0()
        nested_item1 = NSItemNested1()
        nested_item2 = NSItemNested2()
        nested_item3 = NSItemNested3()
        full_nested_item = NSItemFullNested()

        for item in [nested_item0, nested_item1, nested_item2, nested_item3, full_nested_item]:
            item.title = "Title of {}() instance".format(item.__class__.__name__)

        item_with_unique_ns = NSItem0()
        for item in [item_with_unique_ns, nested_item0.elem, full_nested_item.elem0]:
            item.title = "Title of item with unique namespaces"
            item.elem1.attr01 = ""
            item.el_prefix2__elem2.prefix11__attr11 = 0
            item.el_prefix2__elem2.prefix12__attr12 = ""
            item.el_prefix3__elem3.attr21 = "value3_21"
            item.el_prefix3__elem3.pseudo_prefix22__attr22 = 42
            item.el_pseudo_prefix4__elem4.attr01 = ""

        item_with_non_unique_ns = NSItem1()
        for item in [item_with_non_unique_ns, nested_item1.elem, full_nested_item.elem1]:
            item.title = "Title of item with unique namespaces"
            item.elem1.attr01 = "-"
            item.el_prefix__elem2.prefix11__attr11 = -1
            item.el_prefix__elem2.prefix12__attr12 = "-"
            item.elem3.attr21 = "yet another value3_21"
            item.elem3.pseudo_prefix22__attr22 = 4224
            item.el_pseudo_prefix4__elem4.attr01 = "-"
            item.attr = "Some value"

        item_with_non_unique_ns2 = NSItem1()
        item_with_non_unique_ns2.title = "Title of item with unique namespaces 2"
        item_with_non_unique_ns2.elem1.attr01 = "0"
        item_with_non_unique_ns2.el_prefix__elem2.prefix11__attr11 = -999
        item_with_non_unique_ns2.elem3.attr21 = "value"
        item_with_non_unique_ns2.elem3.pseudo_prefix22__attr22 = 42
        item_with_non_unique_ns2.el_pseudo_prefix4__elem4.attr01 = ""

        item_with_same_ns_prefixes = NSItem2()
        for item in [item_with_same_ns_prefixes, nested_item2.el_prefix__elem, full_nested_item.el_prefix2__elem2]:
            item.title = "Title of item with same namespace prefixes"
            item.elem1.attr31 = "Content value 11ё"
            item.prefix__elem2.attr32 = "Attribute value 22"
            item.elem3.attr31 = "Content value 11"
            item.elem3.attr32 = "Attribute value 32"
            item.el_pseudo_prefix4__elem4.attr32 = ""

        item_with_default_nses = NSItem3()
        for item in [item_with_default_nses, nested_item3.el_pseudo_prefix__elem, full_nested_item.elem3]:
            item.title = "Title of item with default namespaces"
            item.elem1.attr31 = "Content value 11ё"
            item.elem2.attr32 = "Attribute value 22"
            item.elem3.attr31 = "Content value 11"
            item.elem3.attr32 = "Attribute value 32"
            item.el_pseudo_prefix4__elem3.attr32 = ""
            item.elem4.attr41 = "A41 b"
            item.elem4.prefix42__attr41 = "0"

        item_with_non_unique_ns_attrs = NSItem4()
        item_with_non_unique_ns_attrs.title = "Title of item with non-unique namespaces in attributes"
        item_with_non_unique_ns_attrs.elem1.attr01 = "#"
        item_with_non_unique_ns_attrs.el_prefix__elem2.prefix11__attr11 = -71
        item_with_non_unique_ns_attrs.el_prefix__elem2.prefix12__attr12 = "+"
        item_with_non_unique_ns_attrs.elem3.attr21 = "yet another value3_21 here"
        item_with_non_unique_ns_attrs.elem3.pseudo_prefix22__attr22 = 1224
        item_with_non_unique_ns_attrs.el_pseudo_prefix4__elem4.attr01 = "+-"
        item_with_non_unique_ns_attrs.attr1 = "Attribute value 1"
        item_with_non_unique_ns_attrs.attr2 = "Attribute value 2"


        self.items = {
            'minimal_item': minimal_item,
            'minimal_item2': minimal_item2,
            'minimal_item3': minimal_item3,
            'minimal_item4': minimal_item4,
            'simple_item': simple_item,
            'item_with_single_category': item_with_single_category,
            'item_with_multiple_categories': item_with_multiple_categories,
            'item_with_guid': item_with_guid,
            'full_rss_item': full_rss_item,
            'item_with_unicode': item_with_unicode,
            'item_with_enclosure': item_with_enclosure,
            'item_with_unique_ns': item_with_unique_ns,
            'item_with_non_unique_ns': item_with_non_unique_ns,
            'item_with_same_ns_prefixes': item_with_same_ns_prefixes,
            'item_with_default_nses': item_with_default_nses,
            'item_with_non_unique_ns_attrs': item_with_non_unique_ns_attrs,
            'unicode_item': unicode_item,
            'nested_item0': nested_item0,
            'nested_item1': nested_item1,
            'nested_item2': nested_item2,
            'nested_item3': nested_item3,
            'full_nested_item': full_nested_item,
        }

        self.ns_items_of_same_cls = [
            ('item_with_non_unique_ns5', NSItem1, item_with_non_unique_ns),
            ('item_with_non_unique_ns4', NSItem1, item_with_non_unique_ns2),
        ]
        self.ns_items = [
             ('item_with_unique_ns2',
              [("el_prefix1", "el_id1"), ("prefix01", "id01"), ("el_prefix2", "el_id2"), ("prefix11", "id11"), ("prefix12", "id12")],
              None,
              item_with_unique_ns),
             ('item_with_unique_ns2',
              (("el_prefix1", "el_id1"), ("prefix01", "id01"), ("el_prefix2", "el_id2"), ("prefix11", "id11"), ("prefix12", "id12")),
              tuple(),
              item_with_unique_ns),
             ('item_with_unique_ns2',
              {"el_prefix1": "el_id1","prefix01": "id01", "el_prefix2": "el_id2", "prefix11": "id11", "prefix12": "id12"},
              None,
              item_with_unique_ns),
             ('item_with_unique_ns3', None, NSItem0, item_with_unique_ns),
             ('item_with_unique_ns3',
              None,
              'tests.test_exporter.NSItem0',
              item_with_unique_ns),
             ('item_with_non_unique_ns2',
              [("el_prefix1", "el_id1"), ("prefix01", "id01"), ("prefix11", "id11"), ("prefix12", "id12"), ("prefix22", "id22"), ("el_prefix4", "el_id4")],
              None,
              item_with_non_unique_ns),
             ('item_with_non_unique_ns3',
              {"el_prefix1": "el_id1", "prefix01": "id01", "prefix11": "id11", "prefix12": "id12", "prefix22": "id22"},
              None,
              item_with_non_unique_ns),
             ('item_with_non_unique_ns2', None, NSItem1, item_with_non_unique_ns),
             ('item_with_non_unique_ns2',
              None,
              'tests.test_exporter.NSItem1',
              item_with_non_unique_ns),
             ('item_with_same_ns_prefixes2',
              [("prefix", "el_id1"), ("prefixa", "id32"), ("unused_prefix", "id000")],
              None,
              item_with_same_ns_prefixes),
             ('item_with_same_ns_prefixes2',
              {"prefix": "el_id1", "prefixa": "id32", "unused_prefix": "id000"},
              None,
              item_with_same_ns_prefixes),
             ('item_with_same_ns_prefixes3', None, NSItem2, item_with_same_ns_prefixes),
             ('item_with_same_ns_prefixes3',
              None,
              'tests.test_exporter.NSItem2',
              item_with_same_ns_prefixes),
             ('item_with_default_nses3',
              {'prefixa': 'id32', 'prefix2': 'el_id4'},
              None,
              item_with_default_nses),
             ('item_with_default_nses2',
              None,
              'tests.test_exporter.NSItem3',
              item_with_default_nses),
             ('item_with_default_nses2',
              None,
              NSItem3,
              item_with_default_nses)
        ]
