# -*- coding: utf-8 -*-

import unittest
from itertools import product, combinations
from parameterized import parameterized

from scrapy_rss.meta import Element, ElementAttribute
from tests.elements import ATTR_VALUES

from tests.utils import RssTestCase



class ChildElement0(Element):
    pass

class ChildElement1(Element):
    pass

class ChildElement2(Element):
    pass

class Element0(Element):
    child00 = ChildElement0()
    child01 = ChildElement0()

class Element1(Element0):
    child10 = ChildElement1()
    child11 = ChildElement1()

class Element2(Element1):
    child20 = ChildElement2()
    child21 = ChildElement2()



class ChildElement3(Element):
    child_attr30 = ElementAttribute(is_content=True)
    child_attr31 = ElementAttribute()

class ChildElement4(Element):
    child_attr41 = ElementAttribute(required=True, is_content=True)
    child_attr42 = ElementAttribute()

class ChildElement5(Element):
    child_attr51 = ElementAttribute()
    child_attr52 = ElementAttribute(is_content=True)

class Element3(Element):
    base_attr30 = ElementAttribute()
    base_attr31 = ElementAttribute()
    child_elem30 = ChildElement3()
    child_elem31 = ChildElement3()

class Element4(Element3):
    base_attr40 = ElementAttribute(required=True)
    base_attr41 = ElementAttribute(required=True)
    child_elem40 = ChildElement4()
    child_elem41 = ChildElement4()

class Element5(Element4):
    base_attr50 = ElementAttribute(is_content=True)
    base_attr51 = ElementAttribute()
    child_elem50 = ChildElement5()
    child_elem51 = ChildElement5()


class TestInheritance(RssTestCase):
    def test_inherited_children(self):
        elem = Element2()
        self.assertEqual(len(elem.children), 3*2)
        self.assertEqual(len(elem.attrs), 0)

        self.assertIsInstance(elem.child00, ChildElement0)
        self.assertIsInstance(elem.child01, ChildElement0)
        self.assertIsNot(elem.child00, elem.child01)

        self.assertIsInstance(elem.child10, ChildElement1)
        self.assertIsInstance(elem.child11, ChildElement1)
        self.assertIsNot(elem.child10, elem.child11)

        self.assertIsInstance(elem.child20, ChildElement2)
        self.assertIsInstance(elem.child21, ChildElement2)
        self.assertIsNot(elem.child20, elem.child21)

    @parameterized.expand(range(3, 6))
    def test_inherited_children_with_attrs(self, level):
        elem = Element5()
        self.assertEqual(3*2, len(elem.children))
        self.assertEqual(3*2, len(elem.attrs))
        children_classes = [None, None, None, ChildElement3, ChildElement4, ChildElement5]

        first_child_elem = getattr(elem, 'child_elem{}0'.format(level))
        second_child_elem = getattr(elem, 'child_elem{}1'.format(level))
        self.assertIsInstance(first_child_elem, children_classes[level])
        self.assertIsInstance(second_child_elem, children_classes[level])
        self.assertIsNot(first_child_elem, second_child_elem)

        first_base_attr = getattr(elem, '__base_attr{}0'.format(level))
        second_base_attr = getattr(elem, '__base_attr{}1'.format(level))
        self.assertIsNotNone(first_base_attr, msg="No attribute <base_attr{}0> in Element5".format(level))
        self.assertIsInstance(first_base_attr, ElementAttribute,
                              msg="Bad attribute <base_attr{}0> of Element5".format(level))
        self.assertIsNotNone(second_base_attr, msg="No attribute <base_attr{}1> in Element5".format(level))
        self.assertIsInstance(second_base_attr, ElementAttribute,
                              msg="Bad attribute <base_attr{}1> of Element5".format(level))
        self.assertIsNot(first_base_attr, second_base_attr)

    @parameterized.expand(('base_attr{}{}'.format(level, idx), value)
                          for level in range(3, 6)
                          for idx in range(2)
                          for value in ATTR_VALUES)
    def test_inherited_attr_init(self, attr_name, attr_value):
        elem = Element5()
        setattr(elem, attr_name, attr_value)
        actual_value = getattr(elem, attr_name)
        self.assertEqual(attr_value, actual_value)

    @parameterized.expand((unpack,
                           {'base_attr{}{}'.format(level, idx): values[2*(level-3) + idx]
                            for level in range(3, 6)
                            for idx in range(2)},)
                          for values in combinations(ATTR_VALUES + ATTR_VALUES, 3*2)
                          for unpack in (True, False))
    def test_inherited_attrs_init_from_dict(self, unpack, dict_value):
        if unpack:
            elem = Element5(**dict_value)
        else:
            elem = Element5(dict_value)
        for attr_name, expected_value in dict_value.items():
            actual_value = getattr(elem, attr_name)
            self.assertEqual(expected_value, actual_value)

    @parameterized.expand(('child_elem{}{}'.format(level, idx), value)
                          for level in range(3, 6)
                          for idx in range(2)
                          for value in ATTR_VALUES)
    def test_inherited_elem_init(self, elem_name, value):
        elem = Element5()
        setattr(elem, elem_name, value)
        child = getattr(elem, elem_name)
        actual_value = getattr(child, str(child.content_arg))
        self.assertEqual(value, actual_value)

    @parameterized.expand((unpack,
                           {'child_elem{}{}'.format(level, idx): values[2*(level-3) + idx]
                            for level in range(3, 6)
                            for idx in range(2)},)
                          for values in combinations(ATTR_VALUES + ATTR_VALUES, 3*2)
                          for unpack in (True, False))
    def test_inherited_elems_init_from_dict(self, unpack, dict_value):
        if unpack:
            elem = Element5(**dict_value)
        else:
            elem = Element5(dict_value)
        for elem_name, expected_value in dict_value.items():
            child = getattr(elem, elem_name)
            actual_value = getattr(child, str(child.content_arg))
            self.assertEqual(expected_value, actual_value)


if __name__ == "__main__":
    unittest.main()
