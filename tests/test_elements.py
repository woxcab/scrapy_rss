# -*- coding: utf-8 -*-

import unittest
from parameterized import parameterized
from itertools import chain, product, combinations, permutations
import re
from copy import deepcopy
import six
import sys

from tests.utils import RssTestCase, get_dict_attr

from scrapy_rss.items import RssItem
from scrapy_rss.elements import *
from scrapy_rss.meta import ItemElementAttribute, ItemElement, MultipleElements
from scrapy_rss.exceptions import InvalidElementValueError


ns_attrs = {'attr1': ItemElementAttribute(ns_prefix='prefix1', ns_uri='id1'),
            'prefix2__attr2': ItemElementAttribute(ns_uri='id2'),
            'prefix3__attr3': ItemElementAttribute(ns_prefix='prefix3', ns_uri='id3'),
            'pseudo_prefix4__attr4': ItemElementAttribute(ns_prefix='prefix4', ns_uri='id4')}

ns_elem_names = {'elem1': {'ns_prefix': 'el_prefix1', 'ns_uri': 'el_id1'},
                 'el_prefix2__elem2': {'ns_uri': 'el_id2'},
                 'el_prefix3__elem3': {'ns_prefix': 'el_prefix3', 'ns_uri': 'el_id3'},
                 'el_pseudo_prefix4__elem4': {'ns_prefix': 'el_prefix4', 'ns_uri': 'el_id4'},}

values = [None, 0, 1, '', '1', 'long текст']


class TestRepr(RssTestCase):
    @parameterized.expand((value, required, is_content, ns_prefix, ns_uri)
                          for value in values
                          for required in (True, False)
                          for is_content in (True, False)
                          for ns_prefix in (None, '', 'prefix')
                          for ns_uri in (('id',) if ns_prefix else (None, '', 'id'))
                          if not is_content or not ns_uri)
    def test_attribute(self, value, required, is_content, ns_prefix, ns_uri):
        attr = ItemElementAttribute(value=value, required=required, is_content=is_content,
                                    ns_prefix=ns_prefix, ns_uri=ns_uri)
        six.assertRegex(
            self,
            repr(attr),
            r'^ItemElementAttribute\(value={}, serializer=[^,]+, required={}, is_content={}, ns_prefix={}, ns_uri={}\)$'
            .format(re.escape(repr(value)), re.escape(repr(required)), re.escape(repr(is_content)),
                    re.escape(repr(ns_prefix or '')), re.escape(repr(ns_uri or ''))))

    @parameterized.expand((attr_name, attr, elem_kwargs)
                          for attr_name, attr in chain([("attr0", ItemElementAttribute())], ns_attrs.items())
                          for elem_kwargs in chain([{}], ns_elem_names.values()))
    def test_element_with_single_attr(self, attr_name, attr, elem_kwargs):
        elem_cls_name = "Element0"
        elem_cls = type(elem_cls_name, (ItemElement,), {attr_name: attr})
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
        chain([("attr0", ItemElementAttribute())], ns_attrs.items()),
        3),
        chain([{}], ns_elem_names.values())))
    def test_element_with_multiple_attrs(self, attrs, elem_kwargs):
        attrs = dict(attrs)
        elem_cls_name = "Element0"
        elem_cls = type(elem_cls_name, (ItemElement,), deepcopy(attrs))
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
                          for attr_name, attr in chain([("attr0", ItemElementAttribute())], ns_attrs.items())
                          for elem_name, elem_kwargs in chain([('elem0', {})], ns_elem_names.items()))
    def test_item_with_single_elem(self, attr_name, attr, elem_name, elem_kwargs):
        elem_cls_name = "Element0"
        item_cls_name = "Item0"
        elem_cls = type(elem_cls_name, (ItemElement,), {attr_name: attr})
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
        combinations(chain([("attr0", ItemElementAttribute())], ns_attrs.items()), 3),
        combinations(chain([("elem0", {})], ns_elem_names.items()), 3)))
    def test_item_with_multiple_elems(self, attrs, elems_descr):
        elems_names, elems_kwargs = zip(*elems_descr)
        item_cls_name = "Item0"
        elem_clses = [type("Element{}".format(n), (ItemElement,), dict(attrs))
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
        elem1 = elem.__class__() if not isinstance(elem, MultipleElements) else elem.__class__(ItemElement)
        elem2 = elem.__class__() if not isinstance(elem, MultipleElements) else elem.__class__(ItemElement)
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
                          for value in values)
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
            elem_cls(ItemElement)
        else:
            elem_cls()

    @parameterized.expand((elem, str(attr), value)
                          for elem in RssItem().elements.values()
                          for attr in elem.attrs
                          for value in values
                          if not isinstance(elem, MultipleElements))
    def test_element_init_with_single_kwarg(self, elem, attr_name, value):
        elem_cls = elem.__class__
        elem_cls(**{attr_name: value})

    @parameterized.expand((elem, str(bad_attr), value)
                          for elem in RssItem().elements.values()
                          for bad_attr in chain(('impossible_attr',),
                                                set(attr for elem in RssItem().elements.values() for attr in elem.attrs)
                                                - set(elem.attrs))
                          for value in values
                          if not isinstance(elem, MultipleElements))
    def test_element_init_with_bad_kwarg(self, elem, bad_attr_name, value):
        elem_cls = elem.__class__
        with six.assertRaisesRegex(self, ValueError, 'supports only the next named arguments',
                                     msg="Invalid attribute '{}' was passed to '{}' initializer"
                                         .format(bad_attr_name, elem_cls.__name__)):
            elem_cls(**{bad_attr_name: value})

    @parameterized.expand((elem, value)
                          for elem in RssItem().elements.values()
                          for value in values
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
                          for value1, value2 in zip(values, values)
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
                          for value in values)
    def test_element_setattr(self, elem_name, attr_name, value):
        item = RssItem()
        elem = getattr(item, elem_name)
        setattr(elem, attr_name, value)
        self.assertEqual(getattr(elem, attr_name), value)

    def test_multi_content_element(self):
        with six.assertRaisesRegex(self, ValueError, r"More than one attributes.*as content"):
            class Element0(ItemElement):
                attr1 = ItemElementAttribute(is_content=True)
                attr2 = ItemElementAttribute(is_content=False)
                attr3 = ItemElementAttribute(is_content=True)


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
        with six.assertRaisesRegex(self, AttributeError, 'have not been assigned'):
            me.category
        me.add(['first', 'second'])
        with six.assertRaisesRegex(self, AttributeError, 'Cannot get attribute: more than one elements'):
            me.category
        with six.assertRaisesRegex(self, AttributeError, 'Cannot set attribute: 2 elements have been assigned'):
            me.category = 'another'

        me.clear()
        me.add('single')
        me.category = 'another'
        self.assertEqual(me.category, 'another')

        item = RssItem()
        with six.assertRaisesRegex(self, AttributeError, 'have not been assigned'):
            item.category.category
        item.category = ['first', 'second']
        with six.assertRaisesRegex(self, AttributeError, 'Cannot get attribute: more than one elements'):
            item.category.category
        with six.assertRaisesRegex(self, AttributeError, 'Cannot set attribute: 2 elements have been assigned'):
            item.category.category = 'other'

        item.category.clear()
        item.category = 'single'
        item.category.category = 'another'
        self.assertEqual(item.category.category, 'another')


class TestNamespacedElements(RssTestCase):
    @parameterized.expand((elem_name, ns_kwargs, attr_name, attr)
                          for elem_name, ns_kwargs in ns_elem_names.items()
                          for attr_name, attr in ns_attrs.items())
    def test_access_by_name(self, elem_name, ns_kwargs, attr_name, attr):
        elem_cls = type("Element0", (ItemElement,), {attr_name: attr})
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
                          for elem_name in ns_elem_names
                          for attr_name, attr in ns_attrs.items())
    def test_attr_namespace(self, elem_name, attr_name, attr):
        elem_cls = type("Element0", (ItemElement,), {attr_name: attr})
        elem = elem_cls()
        actual_attr = next(iter(elem.attrs.values()))
        self.assertIs(actual_attr, getattr(elem, "__" + attr_name))
        self.assertEqual(actual_attr.ns_prefix,
                         attr.ns_prefix or attr_name.split("__")[0])
        self.assertEqual(actual_attr.ns_uri, attr.ns_uri)


    @parameterized.expand(zip(ns_elem_names.values()))
    def test_content_attr_namespace(self, ns_kwargs):
        with six.assertRaisesRegex(self, ValueError, "Content cannot have namespace"):
            ItemElementAttribute(is_content=True, **ns_kwargs)


    @parameterized.expand((elem_name, ns_kwargs, attr_name, attr)
                          for elem_name, ns_kwargs in ns_elem_names.items()
                          for attr_name, attr in ns_attrs.items())
    def test_elem_namespace(self, elem_name, ns_kwargs, attr_name, attr):
        elem_cls = type("Element0", (ItemElement,), {attr_name: attr})
        elem = elem_cls(**ns_kwargs)
        item_cls = type("Item0", (RssItem,), {elem_name: elem})
        item = item_cls()
        actual_elem = next(v for n, v in item.elements.items() if str(n) == elem_name)
        self.assertIs(actual_elem, getattr(item, elem_name))
        self.assertEqual(actual_elem.ns_prefix,
                         ns_kwargs.get("ns_prefix", elem_name.split("__")[0]))
        self.assertEqual(actual_elem.ns_uri, ns_kwargs["ns_uri"])


    @parameterized.expand(combinations(ns_attrs.values(), 1))
    def test_attr_get_namespaces(self, attr):
        actual_namespaces = attr.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, {(attr.ns_prefix, attr.ns_uri)})
        
        actual_namespaces = attr.get_namespaces(False)
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, {(attr.ns_prefix, attr.ns_uri)})


    @parameterized.expand((elem_name, ns_kwargs, deepcopy(attrs))
                          for elem_name, ns_kwargs in ns_elem_names.items()
                          for attrs in chain(combinations(ns_attrs.items(), 1),
                                             combinations(ns_attrs.items(), 2),
                                             combinations(ns_attrs.items(), 3)))
    def test_elem_get_namespaces_with_value(self, elem_name, ns_kwargs, attrs):
        elem_cls = type("Element0", (ItemElement,), dict(attrs))
        elem_kwargs = ns_kwargs.copy()
        elem_kwargs.update({str(attr_name): "" for attr_name, _ in attrs})
        elem = elem_cls(**elem_kwargs)
        expected_namespaces = {(attr.ns_prefix, attr.ns_uri) for _, attr in attrs}
        expected_namespaces.add((ns_kwargs.get("ns_prefix", ""), ns_kwargs["ns_uri"]))
        actual_namespaces = elem.get_namespaces()
        self.assertIsInstance(actual_namespaces, set)
        self.assertEqual(actual_namespaces, expected_namespaces)


    @parameterized.expand((elem_name, ns_kwargs, deepcopy(attrs))
                          for elem_name, ns_kwargs in ns_elem_names.items()
                          for attrs in chain(combinations(ns_attrs.items(), 1),
                                             combinations(ns_attrs.items(), 2),
                                             combinations(ns_attrs.items(), 3)))
    def test_elem_get_namespaces_without_value(self, elem_name, ns_kwargs, attrs):
        elem_cls = type("Element0", (ItemElement,), dict(attrs))
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
        class Element0(ItemElement):
            attr01 = ItemElementAttribute(ns_prefix="prefix01", ns_uri="id01")

        class Element1(ItemElement):
            prefix11__attr11 = ItemElementAttribute(ns_uri="id11")
            prefix12__attr12 = ItemElementAttribute(ns_prefix="prefix12", ns_uri="id12")

        class Element2(ItemElement):
            attr21 = ItemElementAttribute(ns_prefix="prefix21", ns_uri="id01")
            pseudo_prefix22__attr22 = ItemElementAttribute(ns_prefix="prefix22", ns_uri="id22")
        
        class Item0(RssItem):
            elem0 = ItemElement()
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
        class Element0(ItemElement):
            attr00 = ItemElementAttribute(is_content=True)

        class Element1(ItemElement):
            attr10 = ItemElementAttribute(ns_prefix="prefix10", ns_uri="id10")
        
        class Item0(RssItem):
            elem0 = ItemElement()
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


if __name__ == "__main__":
    unittest.main()
