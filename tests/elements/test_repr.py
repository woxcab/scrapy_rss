# -*- coding: utf-8 -*-

import unittest
from parameterized import parameterized
from itertools import chain, product, combinations, permutations
import re
from copy import deepcopy
import six
import sys

from tests.utils import RssTestCase, get_dict_attr, full_name_func
from tests.elements import NS_ATTRS, NS_ELEM_NAMES, ATTR_VALUES

from scrapy_rss.items import RssItem
from scrapy_rss.meta import ElementAttribute, Element, MultipleElements


class TestRepr(RssTestCase):
    @parameterized.expand(((value, required, is_content, ns_prefix, ns_uri)
                           for value in ATTR_VALUES
                           for required in (True, False)
                           for is_content in (True, False)
                           for ns_prefix in (None, '', 'prefix')
                           for ns_uri in (('id',) if ns_prefix else (None, '', 'id'))
                           if not is_content or not ns_uri),
                          name_func=full_name_func)
    def test_attribute(self, value, required, is_content, ns_prefix, ns_uri):
        attr = ElementAttribute(value=value, required=required, is_content=is_content,
                                ns_prefix=ns_prefix, ns_uri=ns_uri)
        six.assertRegex(
            self,
            repr(attr),
            r'^ElementAttribute\(value={}, serializer=[^,]+, required={}, is_content={}, ns_prefix={}, ns_uri={}\)$'
            .format(re.escape(repr(value)), re.escape(repr(required)), re.escape(repr(is_content)),
                    re.escape(repr(ns_prefix or '')), re.escape(repr(ns_uri or ''))))

    if six.PY3:
        def test_partial_init_attribute(self):
            try:
                ElementAttribute(is_content=True, ns_uri='id')
            except ValueError as e:
                attr = e.__traceback__.tb_next.tb_frame.f_locals['self']
                self.assertIsInstance(attr, ElementAttribute)
                self.assertEqual("ElementAttribute(ns_prefix='', ns_uri='id')", repr(attr))


    @parameterized.expand(((required, attr_name, attr, elem_kwargs)
                           for attr_name, attr in chain([("attr0", ElementAttribute())], NS_ATTRS.items())
                           for elem_kwargs in chain([{}], NS_ELEM_NAMES.values())
                           for required in (False, True)),
                          name_func=full_name_func)
    def test_element_with_single_attr(self, required, attr_name, attr, elem_kwargs):
        elem_cls_name = "Element0"
        elem_cls = type(elem_cls_name, (Element,), {attr_name: attr})
        elem = elem_cls(required=required, **elem_kwargs)
        full_elem_kwargs = {"ns_prefix": "", "ns_uri": ""}
        full_elem_kwargs.update(elem_kwargs)
        expected_kwargs_reprs = [", {}={!r}".format(k, v) for k, v in full_elem_kwargs.items()]
        elem_reprs = ["{}(required={!r}, {}={!r}{})".format(elem_cls_name,
                                                            required,
                                                            attr_name,
                                                            attr,
                                                            "".join(expected_kwargs_repr))
                      for expected_kwargs_repr in permutations(expected_kwargs_reprs)]
        assert any(repr(elem) == elem_repr for elem_repr in elem_reprs),\
            "{!r}\nis not equal to one of:\n{}".format(elem, "\n".join(elem_reprs))


    @parameterized.expand(
        product(
            (False, True),
            combinations(chain([("attr0", ElementAttribute())], NS_ATTRS.items()),
                         3),
            chain([{}], NS_ELEM_NAMES.values())
        ),
        name_func=full_name_func)
    def test_element_with_multiple_attrs(self, required, attrs, elem_kwargs):
        attrs = dict(attrs)
        elem_cls_name = "Element0"
        elem_cls = type(elem_cls_name, (Element,), deepcopy(attrs))
        elem = elem_cls(required=required, **elem_kwargs)
        full_elem_kwargs = {"ns_prefix": "", "ns_uri": ""}
        full_elem_kwargs.update(elem_kwargs)
        for attr_name, attr in attrs.items():
            if not attr.ns_prefix and "__" in attr_name:
                attr.ns_prefix = attr_name.split("__")[0]
        expected_kwargs_reprs = [", {}={!r}".format(k, v) for k, v in full_elem_kwargs.items()]
        attrs_reprs = ["{}={!r}".format(name, attr) for name, attr in attrs.items()]
        elem_reprs = ["{}(required={!r}, {}{})".format(elem_cls_name,
                                                       required,
                                                       ", ".join(attrs_repr),
                                                       "".join(expected_kwargs_repr))
                      for attrs_repr in permutations(attrs_reprs)
                      for expected_kwargs_repr in permutations(expected_kwargs_reprs)]
        assert any(repr(elem) == elem_repr for elem_repr in elem_reprs),\
            "{!r}\nis not equal to one of:\n{}".format(elem, "\n".join(elem_reprs))

    if six.PY3:
        def test_partial_init_element(self):
            try:
                Element(1, 2)
            except ValueError as e:
                attr = e.__traceback__.tb_next.tb_frame.f_locals['self']
                self.assertIsInstance(attr, Element)
                self.assertEqual("Element(ns_prefix='', ns_uri='')", repr(attr))


    @parameterized.expand(((attr_name, attr, elem_name, elem_kwargs)
                           for attr_name, attr in chain([("attr0", ElementAttribute())], NS_ATTRS.items())
                           for elem_name, elem_kwargs in chain([('elem0', {})], NS_ELEM_NAMES.items())),
                          name_func=full_name_func)
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
            assert repr(item) == "{}(required=False, {}, ns_prefix='', ns_uri='')".format(
                item_cls_name, ", ".join(default_elems_repr)
            )


    @parameterized.expand(
        product(
            (False, True),
            combinations(chain([("attr0", ElementAttribute())], NS_ATTRS.items()), 3),
            combinations(chain([("elem0", {})], NS_ELEM_NAMES.items()), 3)
        ),
        name_func=full_name_func)
    def test_item_with_multiple_elems(self, required, attrs, elems_descr):
        elems_names, elems_kwargs = zip(*elems_descr)
        item_cls_name = "Item0"
        elem_clses = [type("Element{}".format(n), (Element,), dict(attrs))
                      for n in range(len(elems_descr))]
        elem_instances = [elem_cls(**elems_kwargs[n])
                          for n, elem_cls in enumerate(elem_clses)]
        item_cls = type(item_cls_name, (RssItem,), dict(zip(elems_names, elem_instances)))
        item = item_cls(required=required)
        repr(item)
        if sys.version_info >= (3, 7): # insertion ordered dict
            elems_reprs = ("{}={}".format(elem_name, elem)
                           for elem_name, elem in chain(RssItem().elements.items(),
                                                        zip(elems_names, elem_instances)))
            item_repr = "{}(required={!r}, {}, ns_prefix='', ns_uri='')".format(
                item_cls_name, required, ", ".join(elems_reprs)
            )
            assert repr(item) == item_repr

    if six.PY3:
        def test_partial_init_multiple_elems(self):
            try:
                MultipleElements(str)
            except TypeError as e:
                attr = e.__traceback__.tb_next.tb_frame.f_locals['self']
                self.assertIsInstance(attr, Element)
                self.assertEqual("MultipleElements(ns_prefix='', ns_uri='')", repr(attr))


    @parameterized.expand(
        product(
            (False, True),
            product(ATTR_VALUES, repeat=2),
            product(*([{'prefix': '', 'uri': ''},
                       {'prefix': 'pre_fix{}'.format(n),
                        'uri': 'http://example{}.com'.format(n)}]
                      for n in range(4)))
        ),
        name_func=full_name_func)
    def test_nested_element(self, required_elem01, attr_values, ns):
        class Element1(Element):
            attr10 = ElementAttribute(ns_prefix=ns[3]['prefix'], ns_uri=ns[3]['uri'])

        class Element0(Element):
            attr00 = ElementAttribute(ns_prefix=ns[1]['prefix'], ns_uri=ns[1]['uri'])
            elem01 = Element1(required=required_elem01, ns_prefix=ns[2]['prefix'], ns_uri=ns[2]['uri'])

        elem = Element0(ns_prefix=ns[0]['prefix'], ns_uri=ns[0]['uri'])
        elem.attr00 = attr_values[0]
        elem.elem01.attr10 = attr_values[1]

        repr(elem)
        if sys.version_info >= (3, 7): # insertion ordered dict
            expected_repr = "Element0(required=False, attr00=ElementAttribute(value={attr_values[0]!r}, serializer={attr_serializer!r}, required=False, is_content=False, ns_prefix={ns[1][prefix]!r}, ns_uri={ns[1][uri]!r}), elem01=Element1(required={req!r}, attr10=ElementAttribute(value={attr_values[1]!r}, serializer={attr_serializer!r}, required=False, is_content=False, ns_prefix={ns[3][prefix]!r}, ns_uri={ns[3][uri]!r}), ns_prefix={ns[2][prefix]!r}, ns_uri={ns[2][uri]!r}), ns_prefix={ns[0][prefix]!r}, ns_uri={ns[0][uri]!r})".format(attr_values=attr_values, attr_serializer=ElementAttribute().serializer, ns=ns, req=required_elem01)
            self.assertEqual(expected_repr, repr(elem))



if __name__ == "__main__":
    unittest.main()
