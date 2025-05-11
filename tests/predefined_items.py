# -*- coding: utf-8 -*-
from scrapy_rss.meta import ItemElement, ItemElementAttribute
from scrapy_rss import RssItem


class PredefinedItems(object):
    def __init__(self, *args, **kwargs):
        class NSElement0(ItemElement):
            attr01 = ItemElementAttribute(ns_prefix="prefix01", ns_uri="id01")

        class NSElement1(ItemElement):
            prefix11__attr11 = ItemElementAttribute(ns_uri="id11")
            prefix12__attr12 = ItemElementAttribute(ns_prefix="prefix12", ns_uri="id12")

        class NSElement2(ItemElement):
            attr21 = ItemElementAttribute(is_content=True)
            pseudo_prefix22__attr22 = ItemElementAttribute(ns_prefix="prefix22", ns_uri="id22")

        class NSElement3(ItemElement):
            attr31 = ItemElementAttribute(is_content=True)
            attr32 = ItemElementAttribute(ns_prefix="prefixa", ns_uri="id32")

        class NSElement4(ItemElement):
            attr41 = ItemElementAttribute()
            prefix42__attr41 = ItemElementAttribute(ns_uri="id42")

        class NSItem0(RssItem):
            elem0 = ItemElement()
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

        PredefinedItems.NSItem0 = NSItem0
        PredefinedItems.NSItem1 = NSItem1
        PredefinedItems.NSItem2 = NSItem2
        PredefinedItems.NSItem3 = NSItem3

        minimal_item = RssItem()
        minimal_item.title = 'Title of minimal item'

        minimal_item2 = RssItem()
        minimal_item2.description = 'Description of minimal item'

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

        item_with_unique_ns = NSItem0()
        item_with_unique_ns.title = "Title of item with unique namespaces"
        item_with_unique_ns.elem1.attr01 = ""
        item_with_unique_ns.el_prefix2__elem2.prefix11__attr11 = 0
        item_with_unique_ns.el_prefix2__elem2.prefix12__attr12 = ""
        item_with_unique_ns.el_prefix3__elem3.attr21 = "value3_21"
        item_with_unique_ns.el_prefix3__elem3.pseudo_prefix22__attr22 = 42
        item_with_unique_ns.el_pseudo_prefix4__elem4.attr01 = ""

        item_with_non_unique_ns = NSItem1()
        item_with_non_unique_ns.title = "Title of item with unique namespaces"
        item_with_non_unique_ns.elem1.attr01 = "-"
        item_with_non_unique_ns.el_prefix__elem2.prefix11__attr11 = -1
        item_with_non_unique_ns.el_prefix__elem2.prefix12__attr12 = "-"
        item_with_non_unique_ns.elem3.attr21 = "yet another value3_21"
        item_with_non_unique_ns.elem3.pseudo_prefix22__attr22 = 4224
        item_with_non_unique_ns.el_pseudo_prefix4__elem4.attr01 = "-"

        item_with_non_unique_ns2 = NSItem1()
        item_with_non_unique_ns2.title = "Title of item with unique namespaces 2"
        item_with_non_unique_ns2.elem1.attr01 = "0"
        item_with_non_unique_ns2.el_prefix__elem2.prefix11__attr11 = -999
        item_with_non_unique_ns2.elem3.attr21 = "value"
        item_with_non_unique_ns2.elem3.pseudo_prefix22__attr22 = 42
        item_with_non_unique_ns2.el_pseudo_prefix4__elem4.attr01 = ""

        item_with_same_ns_prefixes = NSItem2()
        item_with_same_ns_prefixes.title = "Title of item with same namespace prefixes"
        item_with_same_ns_prefixes.elem1.attr31 = "Content value 11ё"
        item_with_same_ns_prefixes.prefix__elem2.attr32 = "Attribute value 22"
        item_with_same_ns_prefixes.elem3.attr31 = "Content value 11"
        item_with_same_ns_prefixes.elem3.attr32 = "Attribute value 32"
        item_with_same_ns_prefixes.el_pseudo_prefix4__elem4.attr32 = ""

        item_with_default_nses = NSItem3()
        item_with_default_nses.title = "Title of item with default namespaces"
        item_with_default_nses.elem1.attr31 = "Content value 11ё"
        item_with_default_nses.elem2.attr32 = "Attribute value 22"
        item_with_default_nses.elem3.attr31 = "Content value 11"
        item_with_default_nses.elem3.attr32 = "Attribute value 32"
        item_with_default_nses.el_pseudo_prefix4__elem3.attr32 = ""
        item_with_default_nses.elem4.attr41 = "A41 b"
        item_with_default_nses.elem4.prefix42__attr41 = "0"

        self.items = {
             'minimal_item': minimal_item,
             'minimal_item2': minimal_item2,
             'simple_item': simple_item,
             'item_with_single_category': item_with_single_category,
             'item_with_multiple_categories': item_with_multiple_categories,
             'item_with_guid': item_with_guid,
             'item_with_unicode': item_with_unicode,
             'item_with_enclosure': item_with_enclosure,
             'item_with_unique_ns': item_with_unique_ns,
             'item_with_non_unique_ns': item_with_non_unique_ns,
             'item_with_same_ns_prefixes': item_with_same_ns_prefixes,
             'item_with_default_nses': item_with_default_nses}

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
