# -*- coding: utf-8 -*-

import unittest
from tests.utils import RssTestCase, get_dict_attr
from scrapy_rss.items import RssItem
from scrapy_rss.elements import *
from scrapy_rss.meta import ItemElementAttribute, ItemElement, MultipleElements
from scrapy_rss.exceptions import InvalidElementValueError


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

    def test_uniqueness(self):
        for elem_name, elem in RssItem().elements.items():
            elem1 = elem.__class__() if not isinstance(elem, MultipleElements) else elem.__class__(ItemElement)
            elem2 = elem.__class__() if not isinstance(elem, MultipleElements) else elem.__class__(ItemElement)
            self.assertIsNot(elem1, elem2,
                             msg="Instances of element class '{}' are identical".format(elem.__class__.__name__))

            item1 = RssItem()
            item2 = RssItem()
            self.assertIsNot(getattr(item1, elem_name), getattr(item2, elem_name),
                             msg="Appropriate elements [class '{}'] of RSS item instances are identical"
                                 .format(elem.__class__.__name__))

            for attr_name, attr in elem.attrs.items():
                attr1 = attr.__class__()
                attr2 = attr.__class__()
                self.assertIsNot(attr1, attr2,
                                 msg="Instances of attribute [class '{}'] are identical"
                                     .format(attr.__class__.__name__))

                self.assertIsNot(getattr(getattr(item1, elem_name), '__{}'.format(attr_name)),
                                 getattr(getattr(item2, elem_name), '__{}'.format(attr_name)),
                                 msg="Appropriate attributes [class '{}'] of appropriate elements [class '{}'] "
                                     "of RSS item instances are identical"
                                     .format(attr.__class__.__name__, elem.__class__.__name__))

    def test_item_properties(self):
        item = RssItem()
        for elem_name, elem in item.elements.items():
            for val in (None, 0, '', 1, '1'):
                if elem.required_attrs:
                    with self.assertRaisesRegexp(ValueError, 'Could not assign value'):
                        setattr(item, elem_name, val)
                else:
                    setattr(item, elem_name, val)
                    self.assertEqual(getattr(item, elem_name), val)

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

    def test_element_initializer(self):
        all_attrs = set(attr for elem in RssItem().elements.values() for attr in elem.attrs)
        all_attrs.add('impossible_attr')
        for elem in RssItem().elements.values():
            elem_cls = elem.__class__
            if elem_cls == MultipleElements:
                elem_cls(ItemElement)
                continue
            else:
                elem_cls()
            for attr in elem.attrs:
                elem_cls(**{attr: None})
                elem_cls(**{attr: 0})
                elem_cls(**{attr: ''})
                elem_cls(**{attr: 1})
                elem_cls(**{attr: '1'})
            for bad_attr in all_attrs - set(elem.attrs):
                for val in (None, 0, '', 1, '1'):
                    with self.assertRaisesRegexp(ValueError, 'supports only the next named arguments',
                                                 msg="Invalid attribute '{}' was passed to '{}' initializer"
                                                     .format(bad_attr, elem_cls.__name__)):
                        elem_cls(**{bad_attr: val})
            for val in (None, 0, '', 1, '1'):
                if elem.content_arg:
                    el = elem_cls(val)
                    self.assertEqual(el, getattr(el, el.content_arg))
                    self.assertEqual(el, val)
                else:
                    with self.assertRaisesRegexp(ValueError, 'does not support unnamed arguments',
                                                 msg="Invalid attribute was passed to '{}' initializer "
                                                     "(element must not have content)".format(elem_cls.__name__)):
                        elem_cls(val)

            for val1, val2 in zip((None, 0, '', 1, '1'), (None, 0, '', 1, '1')):
                if elem.content_arg:
                    with self.assertRaisesRegexp(ValueError, 'supports only single unnamed argument',
                                                 msg="Invalid attribute was passed to '{}' initializer "
                                                     "(element must not have content)".format(elem_cls.__name__)):
                        elem_cls(val1, val2)
                else:
                    with self.assertRaisesRegexp(ValueError, 'does not support unnamed arguments',
                                                 msg="Invalid attribute was passed to '{}' initializer "
                                                     "(element must not have content)".format(elem_cls.__name__)):
                        elem_cls(val1, val2)

    def test_element_setattr(self):
        values = [None, 0, 1, '1', 'long string']
        item = RssItem()
        for elem_name in RssItem().elements:
            elem = getattr(item, elem_name)
            for attr in elem.attrs:
                for val in values:
                    setattr(elem, attr, val)
                    self.assertEqual(getattr(elem, attr), val)


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
        me = MultipleElements(ItemElement)
        self.assertEqual(len(me), 0)
        self.assertFalse(me.assigned)
        with self.assertRaises(NotImplementedError):
            me.serialize()
        with self.assertRaises(NotImplementedError):
            MultipleElements(CategoryElement).serialize()

        new_item1 = ItemElement()
        new_item2 = ItemElement()

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
        me.add({'category': self.category_names[0]})
        self.assertEqual(me.category, self.category_names[0])

        me = MultipleElements(CategoryElement)
        me.add([{'category': cat_name} for cat_name in self.category_names])
        self.assertSequenceEqual([el.category for el in me], self.category_names)

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
        item.category = CategoryElement(category=self.category_names[0])
        self.assertEqual(item.category, self.category_names[0])
        for cnt in range(2, 2+len(self.category_names)):
            item.category = [CategoryElement(category=cat_name)
                             for cat_name in self.category_names[:cnt]]
            self.assertEqual(item.category, self.category_names[:cnt])

            item.category = CategoryElement(category=self.category_names[0])
            self.assertEqual(item.category, self.category_names[0])

            item.category = self.category_names[:cnt]
            self.assertEqual(item.category, self.category_names[:cnt])

            item.category = self.category_names[0]
            self.assertEqual(item.category, self.category_names[0])

    def test_irregular_access(self):
        me = MultipleElements(CategoryElement)
        with self.assertRaisesRegexp(AttributeError, 'have not been assigned'):
            me.category
        me.add(['first', 'second'])
        with self.assertRaisesRegexp(AttributeError, 'Cannot get attribute: more than one elements'):
            me.category
        with self.assertRaisesRegexp(AttributeError, 'Cannot set attribute: 2 elements have been assigned'):
            me.category = 'another'

        me.clear()
        me.add('single')
        me.category = 'another'
        self.assertEqual(me.category, 'another')

        item = RssItem()
        with self.assertRaisesRegexp(AttributeError, 'have not been assigned'):
            item.category.category
        item.category = ['first', 'second']
        with self.assertRaisesRegexp(AttributeError, 'Cannot get attribute: more than one elements'):
            item.category.category
        with self.assertRaisesRegexp(AttributeError, 'Cannot set attribute: 2 elements have been assigned'):
            item.category.category = 'other'

        item.category.clear()
        item.category = 'single'
        item.category.category = 'another'
        self.assertEqual(item.category.category, 'another')


if __name__ == '__main__':
    unittest.main()
