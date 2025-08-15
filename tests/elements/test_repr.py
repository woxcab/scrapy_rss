# -*- coding: utf-8 -*-

import unittest
from parameterized import parameterized
from itertools import chain, product, combinations, permutations
import re
from copy import deepcopy
import six
import sys

from tests.utils import RssTestCase, get_dict_attr
from tests.elements import NS_ATTRS, NS_ELEM_NAMES, ATTR_VALUES

from scrapy_rss.items import RssItem
from scrapy_rss.meta import ElementAttribute, Element


class TestRepr(RssTestCase):
    @parameterized.expand((value, required, is_content, ns_prefix, ns_uri)
                          for value in ATTR_VALUES
                          for required in (True, False)
                          for is_content in (True, False)
                          for ns_prefix in (None, '', 'prefix')
                          for ns_uri in (('id',) if ns_prefix else (None, '', 'id'))
                          if not is_content or not ns_uri)
    def test_attribute(self, value, required, is_content, ns_prefix, ns_uri):
        attr = ElementAttribute(value=value, required=required, is_content=is_content,
                                    ns_prefix=ns_prefix, ns_uri=ns_uri)
        six.assertRegex(
            self,
            repr(attr),
            r'^ElementAttribute\(value={}, serializer=[^,]+, required={}, is_content={}, ns_prefix={}, ns_uri={}\)$'
            .format(re.escape(repr(value)), re.escape(repr(required)), re.escape(repr(is_content)),
                    re.escape(repr(ns_prefix or '')), re.escape(repr(ns_uri or ''))))

    @parameterized.expand((attr_name, attr, elem_kwargs)
                          for attr_name, attr in chain([("attr0", ElementAttribute())], NS_ATTRS.items())
                          for elem_kwargs in chain([{}], NS_ELEM_NAMES.values()))
    def test_element_with_single_attr(self, attr_name, attr, elem_kwargs):
        elem_cls_name = "Element0"
        elem_cls = type(elem_cls_name, (Element,), {attr_name: attr})
        elem = elem_cls(**elem_kwargs)
        full_elem_kwargs = {"ns_prefix": "", "ns_uri": ""}
        full_elem_kwargs.update(elem_kwargs)
        expected_kwargs_reprs = [", {}={!r}".format(k, v) for k, v in full_elem_kwargs.items()]
        elem_reprs = ["{}({}={!r}{})".format(elem_cls_name, attr_name, attr,
                                        "".join(expected_kwargs_repr))
                      for expected_kwargs_repr in permutations(expected_kwargs_reprs)]
        assert any(repr(elem) == elem_repr for elem_repr in elem_reprs),\
            "{!r}\nis not equal to one of:\n{}".format(elem, "\n".join(elem_reprs))


    @parameterized.expand(product(combinations(
        chain([("attr0", ElementAttribute())], NS_ATTRS.items()),
        3),
        chain([{}], NS_ELEM_NAMES.values())))
    def test_element_with_multiple_attrs(self, attrs, elem_kwargs):
        attrs = dict(attrs)
        elem_cls_name = "Element0"
        elem_cls = type(elem_cls_name, (Element,), deepcopy(attrs))
        elem = elem_cls(**elem_kwargs)
        full_elem_kwargs = {"ns_prefix": "", "ns_uri": ""}
        full_elem_kwargs.update(elem_kwargs)
        for attr_name, attr in attrs.items():
            if not attr.ns_prefix and "__" in attr_name:
                attr.ns_prefix = attr_name.split("__")[0]
        expected_kwargs_reprs = [", {}={!r}".format(k, v) for k, v in full_elem_kwargs.items()]
        attrs_reprs = ["{}={!r}".format(name, attr) for name, attr in attrs.items()]
        elem_reprs = ["{}({}{})".format(elem_cls_name,
                                        ", ".join(attrs_repr),
                                        "".join(expected_kwargs_repr))
                      for attrs_repr in permutations(attrs_reprs)
                      for expected_kwargs_repr in permutations(expected_kwargs_reprs)]
        assert any(repr(elem) == elem_repr for elem_repr in elem_reprs),\
            "{!r}\nis not equal to one of:\n{}".format(elem, "\n".join(elem_reprs))

    @parameterized.expand((attr_name, attr, elem_name, elem_kwargs)
                          for attr_name, attr in chain([("attr0", ElementAttribute())], NS_ATTRS.items())
                          for elem_name, elem_kwargs in chain([('elem0', {})], NS_ELEM_NAMES.items()))
    def test_item_with_single_elem(self, attr_name, attr, elem_name, elem_kwargs):
        elem_cls_name = "Element0"
        item_cls_name = "Item0"
        elem_cls = type(elem_cls_name, (Element,), {attr_name: attr})
        elem = elem_cls(**elem_kwargs)
        item_cls = type(item_cls_name, (RssItem,), {elem_name: elem})
        item = item_cls()
        repr(item)
        if sys.version_info >= (3, 7): # insertion ordered dict
            default_elems_repr = ("{}={!r}".format(name, value)
                                  for name, value in chain(RssItem().elements.items(),
                                                           [(elem_name, elem)]))
            assert repr(item) == "{}({})".format(item_cls_name,
                                                 ", ".join(default_elems_repr))

    @parameterized.expand(product(
        combinations(chain([("attr0", ElementAttribute())], NS_ATTRS.items()), 3),
        combinations(chain([("elem0", {})], NS_ELEM_NAMES.items()), 3)))
    def test_item_with_multiple_elems(self, attrs, elems_descr):
        elems_names, elems_kwargs = zip(*elems_descr)
        item_cls_name = "Item0"
        elem_clses = [type("Element{}".format(n), (Element,), dict(attrs))
                      for n in range(len(elems_descr))]
        elem_instances = [elem_cls(**elems_kwargs[n])
                          for n, elem_cls in enumerate(elem_clses)]
        item_cls = type(item_cls_name, (RssItem,), dict(zip(elems_names, elem_instances)))
        item = item_cls()
        repr(item)
        if sys.version_info >= (3, 7): # insertion ordered dict
            elems_reprs = ("{}={}".format(elem_name, elem)
                           for elem_name, elem in chain(RssItem().elements.items(),
                                                        zip(elems_names, elem_instances)))
            item_repr = "{}({})".format(item_cls_name, ", ".join(elems_reprs))
            assert repr(item) == item_repr


if __name__ == "__main__":
    unittest.main()
