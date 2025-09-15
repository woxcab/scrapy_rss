# -*- coding: utf-8 -*-

import unittest
from parameterized import parameterized
from itertools import chain, combinations
from copy import deepcopy

import six

from tests.utils import RssTestCase
from tests.elements import NS_ATTRS, NS_ELEM_NAMES, ATTR_VALUES

from scrapy_rss.items import RssItem
from scrapy_rss.meta import BaseNSComponent, ElementAttribute, Element, MultipleElements


class TestNamespacedElements(RssTestCase):
    if six.PY3:
        def tearDown(self):
            if self.id().endswith('test_partial_init_basenscomponent'):
                BaseNSComponent._ns_prefix = ''


        def test_partial_init_basenscomponent(self):
            class BS(BaseNSComponent):
                def __init__(self, *args, **kwargs):
                    raise TypeError

            del BaseNSComponent._ns_prefix

            try:
                BS()
            except TypeError as e:
                comp = e.__traceback__.tb_next.tb_frame.f_locals['self']
                self.assertIsInstance(comp, BaseNSComponent)
                self.assertIn("BS object at 0x", repr(comp))


        def test_partial_init_basenscomponent_after(self):
            self.assertTrue(hasattr(BaseNSComponent, '_ns_prefix'))


    @parameterized.expand((elem_name, ns_kwargs, attr_name, attr)
                          for elem_name, ns_kwargs in NS_ELEM_NAMES.items()
                          for attr_name, attr in NS_ATTRS.items())
    def test_access_by_name(self, elem_name, ns_kwargs, attr_name, attr):
        elem_cls = type("Element0", (Element,), {attr_name: attr})
        elem = elem_cls(**ns_kwargs)
        item_cls = type("Item0", (RssItem,), {elem_name: elem})
        item = item_cls()
        actual_elem = getattr(item, elem_name)
        self.assertIsInstance(actual_elem, elem_cls)
        self.assertIsNot(actual_elem, elem)
        actual_attr_value = getattr(actual_elem, attr_name)
        self.assertIsNone(actual_attr_value, msg="Unexpected attribute value")

        value = "string"
        setattr(actual_elem, attr_name, value)
        actual_attr_value = getattr(actual_elem, attr_name)
        self.assertIs(actual_attr_value, value, msg="Unexpected attribute value")


    @parameterized.expand((elem_name, attr_name, attr)
                          for elem_name in NS_ELEM_NAMES
                          for attr_name, attr in NS_ATTRS.items())
    def test_attr_namespace(self, elem_name, attr_name, attr):
        elem_cls = type("Element0", (Element,), {attr_name: attr})
        elem = elem_cls()
        actual_attr = next(iter(elem.attrs.values()))
        self.assertIs(actual_attr, getattr(elem, "__" + attr_name))
        self.assertEqual(actual_attr.ns_prefix,
                         attr.ns_prefix or attr_name.split("__")[0])
        self.assertEqual(actual_attr.ns_uri, attr.ns_uri)


    @parameterized.expand(zip(NS_ELEM_NAMES.values()))
    def test_content_attr_namespace(self, ns_kwargs):
        with six.assertRaisesRegex(self, ValueError, "Content cannot have namespace"):
            ElementAttribute(is_content=True, **ns_kwargs)


    @parameterized.expand((elem_name, ns_kwargs, attr_name, attr)
                          for elem_name, ns_kwargs in NS_ELEM_NAMES.items()
                          for attr_name, attr in NS_ATTRS.items())
    def test_elem_namespace(self, elem_name, ns_kwargs, attr_name, attr):
        elem_cls = type("Element0", (Element,), {attr_name: attr})
        elem = elem_cls(**ns_kwargs)
        item_cls = type("Item0", (RssItem,), {elem_name: elem})
        item = item_cls()
        actual_elem = next(v for n, v in item.elements.items() if str(n) == elem_name)
        self.assertIs(actual_elem, getattr(item, elem_name))
        self.assertEqual(actual_elem.ns_prefix,
                         ns_kwargs.get("ns_prefix", elem_name.split("__")[0]))
        self.assertEqual(actual_elem.ns_uri, ns_kwargs["ns_uri"])


    @parameterized.expand(combinations(NS_ATTRS.values(), 1))
    def test_attr_get_namespaces(self, attr):
        actual_namespaces = attr.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, set())
        
        actual_namespaces = attr.get_namespaces(False)
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, {(attr.ns_prefix, attr.ns_uri)})


    @parameterized.expand((elem_name, ns_kwargs, deepcopy(attrs))
                          for elem_name, ns_kwargs in NS_ELEM_NAMES.items()
                          for attrs in chain(combinations(NS_ATTRS.items(), 1),
                                             combinations(NS_ATTRS.items(), 2),
                                             combinations(NS_ATTRS.items(), 3)))
    def test_elem_get_namespaces_with_value(self, elem_name, ns_kwargs, attrs):
        elem_cls = type("Element0", (Element,), dict(attrs))
        elem_kwargs = ns_kwargs.copy()
        elem_kwargs.update({str(attr_name): "" for attr_name, _ in attrs})
        elem = elem_cls(**elem_kwargs)
        expected_namespaces = {(attr.ns_prefix, attr.ns_uri) for _, attr in attrs}
        expected_namespaces.add((ns_kwargs.get("ns_prefix", ""), ns_kwargs["ns_uri"]))
        actual_namespaces = elem.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)


    @parameterized.expand((elem_name, ns_kwargs, deepcopy(attrs))
                          for elem_name, ns_kwargs in NS_ELEM_NAMES.items()
                          for attrs in chain(combinations(NS_ATTRS.items(), 1),
                                             combinations(NS_ATTRS.items(), 2),
                                             combinations(NS_ATTRS.items(), 3)))
    def test_elem_get_namespaces_without_value(self, elem_name, ns_kwargs, attrs):
        elem_cls = type("Element0", (Element,), dict(attrs))
        elem = elem_cls(**ns_kwargs)
        actual_namespaces = elem.get_namespaces()
        expected_namespaces = {(ns_kwargs.get("ns_prefix", ""), ns_kwargs["ns_uri"])}
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)

        actual_namespaces = elem.get_namespaces(False)
        expected_namespaces.update({(attr.ns_prefix, attr.ns_uri) for _, attr in attrs})
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)


    def test_item_get_namespaces(self):
        class Element0(Element):
            attr01 = ElementAttribute(ns_prefix="prefix01", ns_uri="id01")

        class Element1(Element):
            prefix11__attr11 = ElementAttribute(ns_uri="id11")
            prefix12__attr12 = ElementAttribute(ns_prefix="prefix12", ns_uri="id12")

        class Element2(Element):
            attr21 = ElementAttribute(ns_prefix="prefix21", ns_uri="id01")
            pseudo_prefix22__attr22 = ElementAttribute(ns_prefix="prefix22", ns_uri="id22")
        
        class Item0(RssItem):
            elem0 = Element()
            elem1 = Element0(ns_prefix="el_prefix1", ns_uri="el_id1")
            el_prefix2__elem2 = Element1(ns_uri="el_id2")
            el_prefix3__elem3 = Element2(ns_prefix="el_prefix3", ns_uri="el_id3")
            el_pseudo_prefix4__elem4 = Element0(ns_prefix="el_prefix4", ns_uri="el_id4")

        item1 = Item0()
        item1.elem1.attr01 = ""
        item1.el_prefix2__elem2.prefix11__attr11 = 0
        item1.el_prefix2__elem2.prefix12__attr12 = ""
        item1.el_prefix3__elem3.attr21 = ""
        item1.el_prefix3__elem3.pseudo_prefix22__attr22 = 0
        item1.el_pseudo_prefix4__elem4.attr01 = ""

        expected_namespaces = {("el_prefix1", "el_id1"), ("prefix01", "id01"),
                               ("el_prefix2", "el_id2"), ("prefix11", "id11"), ("prefix12", "id12"),
                               ("el_prefix3", "el_id3"), ("prefix21", "id01"), ("prefix22", "id22"),
                               ("el_prefix4", "el_id4"), ("prefix01", "id01")}
        actual_namespaces = item1.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)

        item0 = Item0()
        actual_namespaces = item0.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, set())

        actual_namespaces = item0.get_namespaces(False)
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)


    def test_item_get_namespaces_with_multiplied_elems(self):
        class Element0(Element):
            attr00 = ElementAttribute(is_content=True)

        class Element1(Element):
            attr10 = ElementAttribute(ns_prefix="prefix10", ns_uri="id10")
        
        class Item0(RssItem):
            elem0 = Element()
            elem1 = Element1(ns_prefix="el_prefix1", ns_uri="el_id1")
            el_prefix2__elem2 = MultipleElements(Element0, ns_uri="el_id2")
            el_prefix3__elem3 = MultipleElements(Element1, ns_prefix="el_prefix3", ns_uri="el_id3")
            el_pseudo_prefix4__elem4 = MultipleElements(Element0, ns_prefix="el_prefix4", ns_uri="el_id4")
            elem5 = MultipleElements(Element0, ns_prefix="el_prefix5", ns_uri="el_id5")

        
        item = Item0()
        item.elem1.attr10 = ""
        expected_namespaces = {("el_prefix1", "el_id1"), ("prefix10", "id10")}
        actual_namespaces = item.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)


        item = Item0()
        item.el_prefix2__elem2.append("value")
        item.el_prefix3__elem3.extend([{"attr10": "value1"}, {"attr10": "value2"}])
        item.el_pseudo_prefix4__elem4.extend(["value1",
                                              Element0(attr00="value21", ns_uri="el_id4"),
                                              Element0(attr00="value22", ns_prefix="el_prefix4", ns_uri="el_id4"),
                                              {"attr00": "value31", "ns_uri": "el_id4"},
                                              {"attr00": "value32", "ns_prefix": "el_prefix4"},
                                              {"attr00": "value33", "ns_prefix": "el_prefix4", "ns_uri": "el_id4"}])
        item.elem5.extend(["value1", Element0(attr00="value2"), {"attr00": "value3"}])
        expected_namespaces = {("prefix10", "id10"),
                               ("el_prefix2", "el_id2"), ("el_prefix3", "el_id3"),
                               ("el_prefix4", "el_id4"), ("el_prefix5", "el_id5")}
        actual_namespaces = item.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)
        for comp_name, comp in chain(item.attrs.items(), item.children.items()):
            self.assertNotIn('__', comp_name.name)

    def test_namespace_inheritance(self):
        class Element0(Element):
            attr00 = ElementAttribute(is_content=True)

        class Element1(Element):
            attr10 = ElementAttribute(ns_prefix='attr_prefix10', ns_uri='attr_id10')
            attr_prefix11__attr11 = ElementAttribute(ns_uri='attr_id11')
            attr_prefix__attr12 = ElementAttribute(ns_prefix='attr_prefix12', ns_uri='attr_id12')
            elem00 = Element0(ns_prefix='el_prefix10', ns_uri='el_id10')
            el_prefix11__attr11 = Element0(ns_uri='el_id11')
            el_fake_prefix__attr12 = Element0(ns_prefix='el_prefix12', ns_uri='el_id12')

        class Element2(Element1):
            attr_prefix20__attr20 = ElementAttribute(ns_uri='attr_id20')
            el_prefix21__attr11 = Element0(ns_uri='el_id21')

        elem = Element2()
        elem.attr10 = 'attr10'
        elem.attr_prefix11__attr11 = 'attr_prefix11__attr11'
        elem.attr_prefix__attr12 = 'attr_prefix__attr12'
        elem.elem00.attr00 = 'elem00.attr00'
        elem.el_prefix11__attr11.attr00 = 'el_prefix11__attr11.attr00'
        elem.el_fake_prefix__attr12.attr00 = 'el_fake_prefix__attr12.attr00'
        elem.attr_prefix20__attr20 = 'attr_prefix20__attr20'
        elem.el_prefix21__attr11 = 'el_prefix21__attr11.attr00'

        expected_namespaces = {
            ('attr_prefix10', 'attr_id10'), ('attr_prefix11', 'attr_id11'), ('attr_prefix12', 'attr_id12'),
            ('el_prefix10', 'el_id10'), ('el_prefix11', 'el_id11'), ('el_prefix12', 'el_id12'),
            ('attr_prefix20', 'attr_id20'), ('el_prefix21', 'el_id21')
        }
        actual_namespaces = elem.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)
        for comp_name, comp in chain(elem.attrs.items(), elem.children.items()):
            self.assertNotIn('__', comp_name.name, msg="Name {!r} of component {!r} contains namespace prefix".format(comp_name, comp))


if __name__ == "__main__":
    unittest.main()
