# -*- coding: utf-8 -*-

import unittest
from parameterized import parameterized
from itertools import chain
import six

from tests.utils import RssTestCase, get_dict_attr
from tests.elements import NS_ATTRS, NS_ELEM_NAMES, ATTR_VALUES

from scrapy_rss.items import RssItem
from scrapy_rss.exceptions import InvalidAttributeValueError
from scrapy_rss.rss.item_elements import *
from scrapy_rss.meta import ElementAttribute, Element, MultipleElements


class TestSimpleElements(RssTestCase):
    def __init__(self, *args, **kwargs):
        super(TestSimpleElements, self).__init__(*args, **kwargs)

        self.empty_text = ""
        self.non_empty_title = "Non-empty title"
        self.non_empty_description = "Non-empty description"
        self.categories = ["first category name", "second category name",
                           "third category name", "fourth category name"]
        self.unescaped_title = "<b>Non-empty<br/> title</b>"
        self.unescaped_description = "<b>Non-empty description</b><img src='url'/>"

        self.item_with_empty_title_only = RssItem()
        self.item_with_empty_title_only.title = self.empty_text

        self.item_with_empty_description_only = RssItem()
        self.item_with_empty_description_only.description = self.empty_text

        self.item_with_title_only = RssItem()
        self.item_with_title_only.title = self.non_empty_title

        self.item_with_description_only = RssItem()
        self.item_with_description_only.description = self.non_empty_description

        self.item_with_single_category = RssItem()
        self.item_with_single_category.title = self.non_empty_title
        self.item_with_single_category.category = self.categories[0]

        self.item_with_2_categories = RssItem()
        self.item_with_2_categories.title = self.non_empty_title
        self.item_with_2_categories.category = self.categories[:2]

        self.item_with_3_categories = RssItem()
        self.item_with_3_categories.title = self.non_empty_title
        self.item_with_3_categories.category = self.categories[:3]

        self.item_with_4_categories = RssItem()
        self.item_with_4_categories.title = self.non_empty_title
        self.item_with_4_categories.category = self.categories[:4]

        self.item_with_unescaped_text = RssItem()
        self.item_with_unescaped_text.title = self.unescaped_title
        self.item_with_unescaped_text.description = self.unescaped_description

        self.guids = [{'guid': 'identifier 1', 'isPermaLink': False},
                      {'guid': 'identifier 2', 'isPermaLink': True},]

        self.items_with_guid = {0: [], 1: []}

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[0]['guid']
        self.items_with_guid[0].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[0]
        self.items_with_guid[0].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid.guid = self.guids[0]['guid']
        self.items_with_guid[0].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[1]
        self.items_with_guid[1].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[1]['guid']
        item_with_guid.guid.isPermaLink = self.guids[1]['isPermaLink']
        self.items_with_guid[1].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = GuidElement(**self.guids[1])
        self.items_with_guid[1].append(item_with_guid)

    @parameterized.expand((elem, str(elem_name))
                          for elem_name, elem in RssItem().elements.items())
    def test_elements_uniqueness(self, elem, elem_name):
        elem1 = elem.__class__() if not isinstance(elem, MultipleElements) else elem.__class__(Element)
        elem2 = elem.__class__() if not isinstance(elem, MultipleElements) else elem.__class__(Element)
        self.assertIsNot(elem1, elem2,
                         msg="Instances of element class '{}' are identical".format(elem.__class__.__name__))

        item1 = RssItem()
        item2 = RssItem()
        self.assertIsNot(getattr(item1, elem_name), getattr(item2, elem_name),
                         msg="Appropriate elements [class '{}'] of RSS item instances are identical"
                             .format(elem.__class__.__name__))

    @parameterized.expand((elem, str(elem_name), attr, attr_name)
                          for elem_name, elem in RssItem().elements.items()
                          for attr_name, attr in elem.attrs.items())
    def test_attributes_uniqueness(self, elem, elem_name, attr, attr_name):
        item1 = RssItem()
        item2 = RssItem()
        attr1 = attr.__class__()
        attr2 = attr.__class__()
        self.assertIsNot(attr1, attr2,
                         msg="Instances of attribute [class '{}'] are identical"
                             .format(attr.__class__.__name__))

        self.assertIsNot(getattr(getattr(item1, elem_name), attr_name.priv_name),
                         getattr(getattr(item2, elem_name), attr_name.priv_name),
                         msg="Appropriate attributes [class '{}'] of appropriate elements [class '{}'] "
                             "of RSS item instances are identical"
                             .format(attr.__class__.__name__, elem.__class__.__name__))

    @parameterized.expand((elem, str(elem_name), value)
                          for elem_name, elem in RssItem().elements.items()
                          for value in ATTR_VALUES)
    def test_item_properties_v1(self, elem, elem_name, value):
        item = RssItem()
        if elem.required_attrs:
            with six.assertRaisesRegex(self, ValueError, 'Could not assign value'):
                setattr(item, elem_name, value)
        else:
            setattr(item, elem_name, value)
            self.assertEqual(getattr(item, elem_name), value)

    def test_item_properties_v2(self):
        self.assertEqual(self.item_with_empty_title_only.title, self.empty_text)

        self.assertEqual(self.item_with_empty_description_only.description, self.empty_text)

        self.assertEqual(self.item_with_title_only.title, self.non_empty_title)

        self.assertEqual(self.item_with_description_only.description, self.non_empty_description)

        self.assertEqual(self.item_with_single_category.title, self.non_empty_title)
        self.assertEqual(self.item_with_single_category.category, self.categories[0])

        self.assertEqual(self.item_with_3_categories.title, self.non_empty_title)
        self.assertEqual(self.item_with_2_categories.category, self.categories[:2])

        self.assertEqual(self.item_with_4_categories.title, self.non_empty_title)
        self.assertEqual(self.item_with_3_categories.category, self.categories[:3])

        self.assertEqual(self.item_with_4_categories.title, self.non_empty_title)
        self.assertEqual(self.item_with_4_categories.category, self.categories[:4])

        self.assertEqual(self.item_with_unescaped_text.title, self.unescaped_title)

        self.assertEqual(self.item_with_unescaped_text.description, self.unescaped_description)

        for idx, items in self.items_with_guid.items():
            for item in items:
                self.assertEqual(item.guid, self.guids[idx]['guid'])
                self.assertEqual(item.guid.guid, self.guids[idx]['guid'])
                self.assertEqual(item.guid.isPermaLink, self.guids[idx]['isPermaLink'])

    @parameterized.expand((elem,) for elem in RssItem().elements.values())
    def test_element_init_without_args(self, elem):
        elem_cls = elem.__class__
        if elem_cls is MultipleElements:
            elem_cls(Element)
        else:
            elem_cls()

    @parameterized.expand((elem, str(attr), value)
                          for elem in RssItem().elements.values()
                          for attr in elem.attrs
                          for value in ATTR_VALUES
                          if not isinstance(elem, MultipleElements))
    def test_element_init_with_single_kwarg(self, elem, attr_name, value):
        elem_cls = elem.__class__
        elem_cls(**{attr_name: value})

    @parameterized.expand((elem, str(bad_attr), value)
                          for elem in RssItem().elements.values()
                          for bad_attr in chain(('impossible_attr',),
                                                set(attr for elem in RssItem().elements.values() for attr in elem.attrs)
                                                - set(elem.attrs))
                          for value in ATTR_VALUES
                          if not isinstance(elem, MultipleElements))
    def test_element_init_with_bad_kwarg(self, elem, bad_attr_name, value):
        elem_cls = elem.__class__
        with six.assertRaisesRegex(self, ValueError, 'supports only the next named arguments',
                                     msg="Invalid attribute '{}' was passed to '{}' initializer"
                                         .format(bad_attr_name, elem_cls.__name__)):
            elem_cls(**{bad_attr_name: value})

    @parameterized.expand((elem, value)
                          for elem in RssItem().elements.values()
                          for value in ATTR_VALUES
                          if not isinstance(elem, MultipleElements))
    def test_element_init_content_arg(self, elem, value):
        elem_cls = elem.__class__
        if elem.content_arg:
            el = elem_cls(value)
            self.assertEqual(el, getattr(el, str(el.content_arg)))
            self.assertEqual(el, value)
        else:
            with six.assertRaisesRegex(self, ValueError, 'does not support unnamed arguments',
                                         msg="Invalid attribute was passed to '{}' initializer "
                                             "(element must not have content)".format(elem_cls.__name__)):
                elem_cls(value)

    @parameterized.expand((elem, value1, value2)
                          for elem in RssItem().elements.values()
                          for value1, value2 in zip(ATTR_VALUES, ATTR_VALUES)
                          if not isinstance(elem, MultipleElements))
    def test_element_init_with_multiple_args(self, elem, value1, value2):
        elem_cls = elem.__class__
        if elem.content_arg:
            with six.assertRaisesRegex(self, ValueError, 'supports only single unnamed argument',
                                         msg="Invalid attribute was passed to '{}' initializer "
                                             "(element must not have content)".format(elem_cls.__name__)):
                elem_cls(value1, value2)
        else:
            with six.assertRaisesRegex(self, ValueError, 'does not support unnamed arguments',
                                         msg="Invalid attribute was passed to '{}' initializer "
                                             "(element must not have content)".format(elem_cls.__name__)):
                elem_cls(value1, value2)


    @parameterized.expand((str(elem_name), str(attr_name), value)
                          for elem_name, elem_descr in RssItem().elements.items()
                          for attr_name in elem_descr.attrs
                          for value in ATTR_VALUES)
    def test_element_setattr(self, elem_name, attr_name, value):
        item = RssItem()
        elem = getattr(item, elem_name)
        setattr(elem, attr_name, value)
        self.assertEqual(getattr(elem, attr_name), value)

    @parameterized.expand((str(elem_name), str(attr_name), value)
                          for elem_name, elem_descr in RssItem().elements.items()
                          for attr_name in elem_descr.attrs
                          for value in ATTR_VALUES)
    def test_attribute_setattr_from_cls(self, elem_name, attr_name, value):
        item = RssItem()
        elem = getattr(item, elem_name)
        new_attr = ElementAttribute(value)
        with six.assertRaisesRegex(self, InvalidAttributeValueError,
                                   'attribute value cannot be instance of ElementAttribute class'):
            setattr(elem, attr_name, new_attr)

    def test_multi_content_element(self):
        with six.assertRaisesRegex(self, ValueError, r"More than one attributes.*as content"):
            class Element0(Element):
                attr1 = ElementAttribute(is_content=True)
                attr2 = ElementAttribute(is_content=False)
                attr3 = ElementAttribute(is_content=True)


if __name__ == "__main__":
    unittest.main()
