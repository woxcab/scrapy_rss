# -*- coding: utf-8 -*-

import unittest
from itertools import chain, combinations, repeat, product, islice

import six
from parameterized import parameterized

from scrapy_rss import meta
from scrapy_rss.exceptions import InvalidAttributeValueError, InvalidElementValueError, InvalidComponentError
from scrapy_rss.items import FeedItem

from tests.elements import ATTR_URL_VALUES, ATTR_VALUES, NO_NONE_ATTR_VALUES
from tests.utils import RssTestCase, _get_all_attributes_paths, _convert_flat_paths_to_dict_with_values

class UnusedElement(meta.Element):
    attr = meta.ElementAttribute(is_content=True)

class ElementFifthLevel0(meta.Element):
    attr500 = meta.ElementAttribute(is_content=True)

class ElementFourthLevel0(meta.Element):
    attr400 = meta.ElementAttribute(required=True, is_content=True)
    attr401 = meta.ElementAttribute()

class ElementFourthLevel1(meta.Element):
    attr410 = meta.ElementAttribute(required=True)
    elem411 = ElementFifthLevel0()

class ElementFourthLevel3(meta.Element):
    attr430 = meta.ElementAttribute(required=True)
    attr431 = meta.ElementAttribute()
    attr432 = meta.ElementAttribute(required=True)

class ElementThirdLevel0(meta.Element):
    elem300 = ElementFourthLevel0()
    elem301 = ElementFourthLevel1()
    elem302 = ElementFourthLevel3()
    attr303 = meta.ElementAttribute(required=True)
    attr304 = meta.ElementAttribute(required=True)

class ElementSecondLevel0(meta.Element):
    elem200 = ElementThirdLevel0()
    attr201 = meta.ElementAttribute(is_content=True)
    attr202 = meta.ElementAttribute(required=True)

class ElementSecondLevel1(meta.Element):
    elem210 = ElementThirdLevel0()
    attr211 = meta.ElementAttribute(is_content=True)

class ElementFirstLevel0(meta.Element):
    elem100 = ElementSecondLevel0()

class ElementFirstLevel1(meta.Element):
    elem110 = ElementSecondLevel1()

class ItemFirstLevel(FeedItem):
    elem100 = ElementSecondLevel0()

class ElementZeroLevel0(meta.Element):
    elem000 = ElementFirstLevel1()


ATTRIBUTES_PATHS = _get_all_attributes_paths(ElementFirstLevel0())
REQUITED_ATTRIBUTES_PATHS = { # each set is minimal required attributes for valid root
    (
        ('elem100', 'attr202'),
    ), (
        ('elem100', 'elem200', 'attr303'),
        ('elem100', 'elem200', 'attr304'),
        ('elem100', 'attr202'),
    ), (
        ('elem100', 'elem200', 'elem300', 'attr400'),
        ('elem100', 'elem200', 'attr303'),
        ('elem100', 'elem200', 'attr304'),
        ('elem100', 'attr202'),
    ), (
        ('elem100', 'elem200', 'elem301', 'attr410'),
        ('elem100', 'elem200', 'attr303'),
        ('elem100', 'elem200', 'attr304'),
        ('elem100', 'attr202'),
    ), (
        ('elem100', 'elem200', 'elem302', 'attr430'),
        ('elem100', 'elem200', 'elem302', 'attr432'),
        ('elem100', 'elem200', 'attr303'),
        ('elem100', 'elem200', 'attr304'),
        ('elem100', 'attr202'),
    )
}


class TestNestedElements(RssTestCase):
    def __init__(self, *args, **kwargs):
        super(TestNestedElements, self).__init__(*args, **kwargs)

    @parameterized.expand((paths,) for paths in (ATTRIBUTES_PATHS, REQUITED_ATTRIBUTES_PATHS))
    def test_0_predefined_constants(self, paths):
        self.assertTrue(paths, msg='Empty constant')
        for path_idx, path in enumerate(paths):
            self.assertTrue(path, msg='Empty path #{}'.format(path_idx))
            for component_idx, component in enumerate(path):
                self.assertTrue(component,
                                msg='Empty component #{} in the path #{}'.format(component_idx, path_idx))

    @parameterized.expand((elem_cls, leaf_path, value)
                          for value in ATTR_VALUES
                          for elem_cls, leaf_path in ((ElementFirstLevel1, ['elem110', 'attr211']),
                                                      (ElementZeroLevel0, ['elem000', 'elem110', 'attr211'])))
    def test_element_init_child(self, elem_cls, leaf_path, value):
        elem = elem_cls(value)
        comp = elem
        for c in leaf_path:
            comp = getattr(comp, c)
        self.assertEqual(value, comp)

    @parameterized.expand((attr_path, first_value, second_value)
                          for attr_path in ATTRIBUTES_PATHS
                          for first_value in ATTR_VALUES
                          for second_value in ATTR_VALUES)
    def test_parent_elements_is_assigned(self,  attr_path, first_value, second_value):
        root_element = ElementFirstLevel0()
        self.assertFalse(root_element.assigned)
        target_component = root_element
        for component_name in attr_path[:-1]:
            target_component = getattr(target_component, component_name)

        setattr(target_component, attr_path[-1], first_value)
        expected = first_value is not None
        element = root_element
        for component_name in attr_path:
            self.assertIs(element.assigned, expected)
            element = getattr(element, component_name)

        setattr(target_component, attr_path[-1], second_value)
        expected = second_value is not None
        element = root_element
        for component_name in attr_path:
            self.assertIs(element.assigned, expected)
            element = getattr(element, component_name)

    @parameterized.expand((attr_path, first_value, second_value)
                          for attr_path in ATTRIBUTES_PATHS
                          for first_value in ATTR_VALUES
                          for second_value in ATTR_VALUES)
    def test_item_element_is_assigned(self, attr_path, first_value, second_value):
        item = ItemFirstLevel()
        self.assertFalse(getattr(item, attr_path[0]).assigned)
        component = item
        for attr_name in attr_path[:-1]:
            component = getattr(component, attr_name)
        setattr(component, attr_path[-1], first_value)
        self.assertIs(getattr(item, attr_path[0]).assigned, first_value is not None)
        setattr(component, attr_path[-1], second_value)
        self.assertIs(getattr(item, attr_path[0]).assigned, second_value is not None)

    @parameterized.expand((part_paths, value)
                          for value in NO_NONE_ATTR_VALUES
                          for paths in REQUITED_ATTRIBUTES_PATHS if len(paths) > 1
                          for length in range(1, len(paths) - 1)
                          for part_paths in combinations(paths, length)
                          if part_paths not in REQUITED_ATTRIBUTES_PATHS)
    def test_is_valid_false(self, part_required_attrs, value):
        root = ElementFirstLevel0()
        root.validate()
        self.assertTrue(root.is_valid())
        for path in part_required_attrs:
            element = root
            for component in path[:-1]:
                element = getattr(element, component)
            setattr(element, path[-1], value)
            with self.assertRaises(InvalidComponentError):
                root.validate()
            self.assertFalse(root.is_valid(), msg='Bad root valid value on attribute {} of {}'.format(path, part_required_attrs))

    @parameterized.expand((paths, value)
                          for value in NO_NONE_ATTR_VALUES
                          for paths in REQUITED_ATTRIBUTES_PATHS)
    def test_is_valid_true(self, paths, value):
        root = ElementFirstLevel0()
        root.validate()
        self.assertTrue(root.is_valid())
        for path in paths:
            element = root
            for component in path[:-1]:
                element = getattr(element, component)
            setattr(element, path[-1], value)
        root.validate()
        self.assertTrue(root.is_valid(), msg='Bad root valid value when attributes {} is set'.format(paths))

    @parameterized.expand((paths, values)
                          for paths in REQUITED_ATTRIBUTES_PATHS
                          for multi_values in (chain(NO_NONE_ATTR_VALUES,
                                                     reversed(NO_NONE_ATTR_VALUES),
                                                     NO_NONE_ATTR_VALUES,
                                                     reversed(NO_NONE_ATTR_VALUES)),)
                          for values in (list(islice(multi_values, len(paths)))
                                         for _ in range(4*len(NO_NONE_ATTR_VALUES) // len(paths))))
    def test_init_from_dict(self, paths, values):
        self.assertEqual(len(paths), len(values))
        data = _convert_flat_paths_to_dict_with_values([path[1:] for path in paths], values)
        root = ElementFirstLevel0()
        root.elem100 = data
        for path_idx, path in enumerate(paths):
            current_element = root
            for component in path[:-1]:
                current_element = getattr(current_element, component)
            self.assertEqual(values[path_idx], getattr(current_element, path[-1]))

    @parameterized.expand(
        (required1, ns1[0], ns1[1], required2, ns2[0], ns2[1])
        for (required1, required2), (ns1, ns2) in product(product([True, False], repeat=2),
                                                          product([('', ''), ('prefix', 'id')], repeat=2))
    )
    def test_init_from_dict_settings_immutability(self, required1, ns_prefix1, ns_uri1, required2, ns_prefix2, ns_uri2):
        class Element0(meta.Element):
            attr = meta.ElementAttribute(is_content=True)

        class Element1(meta.Element):
            elem1 = Element0(ns_prefix=ns_prefix1, ns_uri=ns_uri1, required=required1)

        elem = Element1()
        elem.elem1 = {'ns_prefix': ns_prefix2, 'ns_uri': ns_uri2, 'required': required2, 'attr': 5}
        self.assertEqual(ns_prefix1, elem.elem1.ns_prefix)
        self.assertEqual(ns_uri1, elem.elem1.ns_uri)
        self.assertEqual(required1, elem.elem1.required)
        self.assertEqual(5, elem.elem1.attr)

    @parameterized.expand((attr_path, value)
                          for attr_path in ATTRIBUTES_PATHS
                          for value in ATTR_VALUES)
    def test_init_from_attr_value(self, attr_path, value):
        root = ElementFirstLevel0()
        attr_name = attr_path[-1]
        element = root
        for component_name in attr_path[:-1]:
            element = getattr(element, component_name)
        setattr(element, attr_name, value)

        component = root
        for component_name in attr_path:
            component = getattr(component, component_name)
        self.assertEqual(value, component)

    @parameterized.expand((attr_path, value)
                          for attr_path in ATTRIBUTES_PATHS
                          for value in ATTR_VALUES)
    def test_init_from_attr_cls(self, attr_path, value):
        root = ElementFirstLevel0()
        attr_name = attr_path[-1]
        element = root
        for component_name in attr_path[:-1]:
            element = getattr(element, component_name)
        new_value = meta.ElementAttribute(value)
        with six.assertRaisesRegex(self, InvalidAttributeValueError,
                                    r'attribute value cannot be instance of ElementAttribute class'):
            setattr(element, attr_name, new_value)

    @parameterized.expand((full_attr_path[:n],
                           full_attr_path[n:],
                           value)
                          for full_attr_path in ATTRIBUTES_PATHS
                          for n in range(1, len(full_attr_path))
                          for value in ATTR_VALUES)
    def test_init_from_elem_cls(self, elem_path, attr_path, value):
        root = ElementFirstLevel0()
        elem_name = elem_path[-1]
        element = root
        for component_name in elem_path[:-1]:
            element = getattr(element, component_name)
        new_elem_cls = getattr(element, elem_path[-1]).__class__
        init_params = {}
        params = init_params
        for idx, component_name in enumerate(attr_path):
            if idx == len(attr_path) - 1:
                params[component_name] = value
            else:
                params[component_name] = {}
                params = params[component_name]
        new_value = new_elem_cls(**init_params)
        setattr(element, elem_name, new_value)

        component = root
        for component_name in chain(elem_path, attr_path):
            component = getattr(component, component_name)
        self.assertEqual(value, component)

        with self.assertRaises(InvalidElementValueError):
            setattr(element, elem_name, UnusedElement(value))



if __name__ == "__main__":
    unittest.main()
