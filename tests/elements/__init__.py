# -*- coding: utf-8 -*-

from scrapy_rss.meta import ElementAttribute


NS_ATTRS = {'attr1': ElementAttribute(ns_prefix='prefix1', ns_uri='id1'),
            'prefix2__attr2': ElementAttribute(ns_uri='id2'),
            'prefix3__attr3': ElementAttribute(ns_prefix='prefix3', ns_uri='id3'),
            'pseudo_prefix4__attr4': ElementAttribute(ns_prefix='prefix4', ns_uri='id4')}

NS_ELEM_NAMES = {'child1': {'ns_prefix': 'el_prefix1', 'ns_uri': 'el_id1'},
                 'el_prefix2__elem2': {'ns_uri': 'el_id2'},
                 'el_prefix3__elem3': {'ns_prefix': 'el_prefix3', 'ns_uri': 'el_id3'},
                 'el_pseudo_prefix4__elem4': {'ns_prefix': 'el_prefix4', 'ns_uri': 'el_id4'}, }

ATTR_VALUES = [None, 0, 1, '', '1', 'long текст']
NO_NONE_ATTR_VALUES = [v for v in ATTR_VALUES if v is not None]

ATTR_URL_VALUES = [None, 'http://example.com/']
