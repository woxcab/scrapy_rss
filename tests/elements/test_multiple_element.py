# -*- coding: utf-8 -*-

import unittest
import six

from tests.utils import RssTestCase

from scrapy_rss.items import RssItem
from scrapy_rss.rss.item_elements import *
from scrapy_rss.meta import Element, MultipleElements



class TestMultipleElements(RssTestCase):
    def __init__(self, *args, **kwargs):
        super(TestMultipleElements, self).__init__(*args, **kwargs)
        self.category_names = ['1st category name', '2nd category name', '3rd category name', '4th category']
        non_empty_title = 'Item title'
        self.item_with_single_category = RssItem()
        self.item_with_single_category.title = non_empty_title
        self.item_with_single_category.category = self.category_names[0]

        self.item_with_2_categories = RssItem()
        self.item_with_2_categories.title = non_empty_title
        self.item_with_2_categories.category = self.category_names[:2]

        self.item_with_3_categories = RssItem()
        self.item_with_3_categories.title = non_empty_title
        self.item_with_3_categories.category = self.category_names[:3]

        self.item_with_4_categories = RssItem()
        self.item_with_4_categories.title = non_empty_title
        self.item_with_4_categories.category = self.category_names[:4]

    def test_methods(self):
        me = MultipleElements(Element)
        self.assertEqual(len(me), 0)
        self.assertFalse(me.assigned)
        with self.assertRaises(NotImplementedError):
            me.serialize_attrs()
        with self.assertRaises(NotImplementedError):
            MultipleElements(CategoryElement).serialize_attrs()

        new_item1 = Element()
        new_item2 = Element()

        me.append(new_item1)
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)
        self.assertIs(me[0], new_item1)

        self.assertIs(me.pop(), new_item1)
        self.assertFalse(me.assigned)
        self.assertEqual(len(me), 0)

        me.extend([new_item1, new_item2])
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 2)
        self.assertIs(me[0], new_item1)
        self.assertIs(me[1], new_item2)

        self.assertIs(me.pop(), new_item2)
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)

        self.assertIs(me.pop(), new_item1)
        self.assertFalse(me.assigned)
        self.assertEqual(len(me), 0)

        me.add(new_item1)
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)

        self.assertIs(me.pop(), new_item1)
        self.assertFalse(me.assigned)
        self.assertEqual(len(me), 0)

        me.add([new_item1, new_item2])
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 2)

        self.assertIs(me.pop(), new_item2)
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)

        self.assertIs(me.pop(), new_item1)
        self.assertFalse(me.assigned)
        self.assertEqual(len(me), 0)

        me.add([new_item1, new_item2])
        self.assertIs(me.pop(0), new_item1)
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)

        self.assertIs(me.pop(0), new_item2)
        self.assertFalse(me.assigned)
        self.assertEqual(len(me), 0)

        me.add([new_item1, new_item2])
        del me[0]
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)
        self.assertIs(me[0], new_item2)

        del me[0]
        self.assertFalse(me.assigned)
        self.assertEqual(len(me), 0)

        me.add(new_item1)
        with self.assertRaises(TypeError):
            me[0] = type('some_class')()
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)
        me[0] = new_item2
        self.assertTrue(me.assigned)
        self.assertEqual(len(me), 1)
        self.assertIs(me[0], new_item2)
        with self.assertRaises(IndexError):
            me[1] = new_item1

    def test_initializer(self):
        with self.assertRaises(TypeError):
            MultipleElements(type('some_non_element_class'))

        me = MultipleElements(CategoryElement)
        me.add({'value': self.category_names[0]})
        self.assertEqual(me.value, self.category_names[0])

        me = MultipleElements(CategoryElement)
        me.add([{'value': cat_name} for cat_name in self.category_names])
        self.assertSequenceEqual([el.value for el in me], self.category_names)

    def test_instances(self):
        self.assertIsInstance(self.item_with_single_category.category, MultipleElements)
        for category in self.item_with_single_category.category:
            self.assertIsInstance(category, CategoryElement)
        self.assertIsInstance(self.item_with_2_categories.category, MultipleElements)
        for category in self.item_with_2_categories.category:
            self.assertIsInstance(category, CategoryElement)
        self.assertIsInstance(self.item_with_3_categories.category, MultipleElements)
        for category in self.item_with_3_categories.category:
            self.assertIsInstance(category, CategoryElement)
        self.assertIsInstance(self.item_with_4_categories.category, MultipleElements)
        for category in self.item_with_4_categories.category:
            self.assertIsInstance(category, CategoryElement)

    def test_inner_cls_attr(self):
        item = RssItem()
        item.category = CategoryElement(value=self.category_names[0])
        self.assertEqual(item.category, self.category_names[0])
        for cnt in range(2, 2+len(self.category_names)):
            item.category = [CategoryElement(value=cat_name)
                             for cat_name in self.category_names[:cnt]]
            self.assertEqual(item.category, self.category_names[:cnt])

            item.category = CategoryElement(value=self.category_names[0])
            self.assertEqual(item.category, self.category_names[0])

            item.category = self.category_names[:cnt]
            self.assertEqual(item.category, self.category_names[:cnt])

            item.category = self.category_names[0]
            self.assertEqual(item.category, self.category_names[0])

    def test_irregular_access(self):
        me = MultipleElements(CategoryElement)
        with six.assertRaisesRegex(self, AttributeError, 'have not been assigned'):
            me.value
        me.add(['first', 'second'])
        with six.assertRaisesRegex(self, AttributeError, 'Cannot get attribute: more than one elements'):
            me.value
        with six.assertRaisesRegex(self, AttributeError, 'Cannot set attribute: 2 elements have been assigned'):
            me.value = 'another'

        me.clear()
        with six.assertRaisesRegex(self, AttributeError, 'have not been assigned'):
            me.value
        me.add('single')
        self.assertEqual(me.value, 'single')
        me.value = 'another'
        self.assertEqual(me.value, 'another')

        me.value = None
        with six.assertRaisesRegex(self, AttributeError, 'have not been assigned'):
            me.value

        item = RssItem()
        with six.assertRaisesRegex(self, AttributeError, 'have not been assigned'):
            item.category.value
        item.category = ['first', 'second']
        with six.assertRaisesRegex(self, AttributeError, 'Cannot get attribute: more than one elements'):
            item.category.value
        with six.assertRaisesRegex(self, AttributeError, 'Cannot set attribute: 2 elements have been assigned'):
            item.category.value = 'other'

        item.category.clear()
        item.category = 'first'
        item.category.value = 'another'
        self.assertEqual(item.category.value, 'another')


if __name__ == "__main__":
    unittest.main()
