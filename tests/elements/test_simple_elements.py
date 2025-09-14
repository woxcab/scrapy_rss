# -*- coding: utf-8 -*-

import unittest
from parameterized import parameterized
from itertools import chain, product, combinations, combinations_with_replacement
from functools import partial
import pytest
import six

from tests import predefined_items
from tests.utils import RssTestCase, get_dict_attr, full_name_func
from tests.elements import NS_ATTRS, NS_ELEM_NAMES, ATTR_VALUES, NO_NONE_ATTR_VALUES

from scrapy_rss.items import RssItem
from scrapy_rss.exceptions import InvalidComponentNameError, InvalidAttributeValueError, InvalidElementValueError
from scrapy_rss.rss.item_elements import *
from scrapy_rss.meta import BaseNSComponent, NSComponentName, ElementAttribute, Element, MultipleElements, FeedItem


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

        self.guids = [{'value': 'identifier 1', 'isPermaLink': True},
                      {'value': 'identifier 2', 'isPermaLink': False}]

        self.items_with_guid = {0: [], 1: []}

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[0]['value']
        self.items_with_guid[0].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[0]
        self.items_with_guid[0].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid.value = self.guids[0]['value']
        self.items_with_guid[0].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[1]
        self.items_with_guid[1].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = self.guids[1]['value']
        item_with_guid.guid.isPermaLink = self.guids[1]['isPermaLink']
        self.items_with_guid[1].append(item_with_guid)

        item_with_guid = RssItem()
        item_with_guid.title = self.non_empty_title
        item_with_guid.guid = GuidElement(**self.guids[1])
        self.items_with_guid[1].append(item_with_guid)

    @parameterized.expand(((elem.__class__, str(elem_name))
                           for elem_name, elem in RssItem().elements.items()),
                          name_func=full_name_func)
    def test_elements_uniqueness(self, elem_cls, elem_name):
        elem1 = elem_cls() if not issubclass(elem_cls, MultipleElements) else elem_cls(Element)
        elem2 = elem_cls() if not issubclass(elem_cls, MultipleElements) else elem_cls(Element)
        self.assertIsNot(elem1, elem2,
                         msg="Instances of element class '{}' are identical".format(elem_cls.__name__))

        item1 = RssItem()
        item2 = RssItem()
        self.assertIsNot(getattr(item1, elem_name), getattr(item2, elem_name),
                         msg="Appropriate elements [class '{}'] of RSS item instances are identical"
                             .format(elem_cls.__name__))

    @parameterized.expand(((elem.__class__, str(elem_name), attr.__class__, attr_name)
                           for elem_name, elem in RssItem().elements.items()
                           for attr_name, attr in elem.attrs.items()),
                          name_func=full_name_func)
    def test_attributes_uniqueness(self, elem_cls, elem_name, attr_cls, attr_name):
        item1 = RssItem()
        item2 = RssItem()
        attr1 = attr_cls()
        attr2 = attr_cls()
        self.assertIsNot(attr1, attr2,
                         msg="Instances of attribute [class '{}'] are identical"
                             .format(attr_cls.__name__))

        self.assertIsNot(getattr(getattr(item1, elem_name), attr_name.priv_name),
                         getattr(getattr(item2, elem_name), attr_name.priv_name),
                         msg="Appropriate attributes [class '{}'] of appropriate elements [class '{}'] "
                             "of RSS item instances are identical"
                             .format(attr_cls.__name__, elem_cls.__name__))

    @parameterized.expand(((elem, str(elem_name), value)
                           for elem_name, elem in RssItem().elements.items()
                           for value in ATTR_VALUES),
                          name_func=full_name_func)
    def test_item_properties_v1(self, elem, elem_name, value):
        item = RssItem()
        if value is not None and set(elem.required_attrs) - ({elem.content_name} or set()):
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
                self.assertEqual(item.guid, self.guids[idx]['value'])
                self.assertEqual(item.guid.value, self.guids[idx]['value'])
                self.assertEqual(item.guid.isPermaLink, self.guids[idx]['isPermaLink'])

    @parameterized.expand((elem.__class__,) for elem in RssItem().elements.values())
    def test_element_init_without_args(self, elem_cls):
        if elem_cls is MultipleElements:
            elem_cls(Element)
        else:
            elem_cls()

    @parameterized.expand(((elem.__class__, str(attr), value)
                           for elem in RssItem().elements.values()
                           for attr in elem.attrs
                           for value in ATTR_VALUES),
                          name_func=full_name_func)
    def test_element_init_with_single_kwarg(self, elem_cls, attr_name, value):
        elem_cls(**{attr_name: value})

    def test_element_init_from_element(self):
        elem = Element()
        with self.assertRaises(NotImplementedError):
            new_elem = Element(elem)

    @parameterized.expand(((elem.__class__, str(bad_attr), value)
                           for elem in RssItem().elements.values()
                           for bad_attr in chain(('impossible_attr',),
                                                 set(attr for elem in RssItem().elements.values() for attr in elem.attrs)
                                                 - set(elem.attrs))
                           for value in ATTR_VALUES
                           if not isinstance(elem, MultipleElements)),
                          name_func=full_name_func)
    def test_element_init_with_bad_kwarg(self, elem_cls, bad_attr_name, value):
        with six.assertRaisesRegex(self, KeyError, 'Element does not support components:',
                                     msg="Invalid attribute '{}' was passed to '{}' initializer"
                                         .format(bad_attr_name, elem_cls.__name__)):
            elem_cls(**{bad_attr_name: value})

    @parameterized.expand(((elem, value)
                           for elem in RssItem().elements.values()
                           for value in ATTR_VALUES
                           if not isinstance(elem, MultipleElements)),
                          name_func=full_name_func)
    def test_element_init_content_name(self, elem, value):
        elem_cls = elem.__class__
        if elem.content_name:
            el = elem_cls(value)
            self.assertEqual(el, getattr(el, str(el.content_name)))
            with pytest.warns(DeprecationWarning, match='Property <content_arg> is deprecated'):
                self.assertEqual(el, getattr(el, str(el.content_arg)))
            self.assertEqual(el, value)
        else:
            with six.assertRaisesRegex(self, ValueError, 'does not support unnamed non-mapping arguments',
                                         msg="Invalid attribute was passed to '{}' initializer "
                                             "(element must not have content)".format(elem_cls.__name__)):
                elem_cls(value)

    @parameterized.expand(((elem.__class__, str(elem.content_name), value1, value2)
                           for elem in RssItem().elements.values()
                           for value1, value2 in combinations(NO_NONE_ATTR_VALUES, 2)
                           if elem.content_name and not isinstance(elem, MultipleElements)),
                          name_func=full_name_func)
    def test_element_init_content_name_and_kwargs(self, elem_cls, content_name, value1, value2):
        elem = elem_cls(value1, **{content_name: value2})
        self.assertEqual(value2, getattr(elem, content_name))

    @parameterized.expand(((elem.__class__, value1, value2)
                           for elem in RssItem().elements.values()
                           for value1, value2 in zip(ATTR_VALUES, ATTR_VALUES)
                           if not isinstance(elem, MultipleElements)),
                          name_func=full_name_func)
    def test_element_init_with_multiple_args(self, elem_cls, value1, value2):
        with six.assertRaisesRegex(self, ValueError, 'supports only single unnamed argument',
                                     msg="Invalid attribute was passed to '{}' initializer "
                                         "(element must not have content)".format(elem_cls.__name__)):
            elem_cls(value1, value2)

    @parameterized.expand(((elem_cls,)
                           for elem in RssItem().elements.values()
                           for elem_cls in (elem.__class__ if not isinstance(elem, MultipleElements)
                                            else partial(elem.__class__, base_element_cls=Element),)),
                          name_func=full_name_func)
    def test_unknown_attribute_setter(self, elem_cls):
        elem = elem_cls()
        with six.assertRaisesRegex(self, AttributeError, 'No attribute'):
            elem.unknown = 5

    @parameterized.expand(((str(elem_name), str(attr_name), value)
                           for elem_name, elem_descr in RssItem().elements.items()
                           for attr_name in elem_descr.attrs
                           for value in ATTR_VALUES),
                          name_func=full_name_func)
    def test_element_setattr(self, elem_name, attr_name, value):
        item = RssItem()
        elem = getattr(item, elem_name)
        setattr(elem, attr_name, value)
        self.assertEqual(getattr(elem, attr_name), value)

    @parameterized.expand(((str(elem_name), str(attr_name), value)
                           for elem_name, elem_descr in RssItem().elements.items()
                           for attr_name in elem_descr.attrs
                           for value in ATTR_VALUES),
                          name_func=full_name_func)
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

    @parameterized.expand(((base_elem_cls, comp_name, comp_cls,
                            (base_elem_cls in {FeedItem, RssItem}
                             or comp_name in meta.ElementMeta._blacklisted_comp_names))
                          for comp_name in (meta.ElementMeta._blacklisted_comp_names
                                            | meta.ItemMeta._blacklisted_comp_names)
                          for base_elem_cls in (Element, MultipleElements, FeedItem, RssItem)
                          for comp_cls in (meta.ElementAttribute, meta.Element)),
                          name_func=full_name_func)
    def test_blacklisted_names0(self, base_elem_cls, comp_name, comp_cls, raising):
        if raising:
            with six.assertRaisesRegex(self, InvalidComponentNameError,
                                       "Cannot use special property <{}> as a component name".format(comp_name)):
                elem_cls0 = type('Element0', (base_elem_cls,), {comp_name: comp_cls()})

            for idx in range(1, 5):
                exp_comp_name = comp_name + '_' * idx
                elem_cls1 = type('Element{}'.format(idx), (base_elem_cls,), {exp_comp_name: comp_cls()})
                elem1 = (elem_cls1(base_element_cls=Element)
                         if issubclass(base_elem_cls, MultipleElements)
                         else elem_cls1())
                actual_comp_name = next(c for c in chain(elem1.attrs, elem1.children)
                                        if str(c) == exp_comp_name)
                self.assertTrue(hasattr(elem1, '__{}'.format(exp_comp_name)),
                                msg='No component with name {!r}'.format(exp_comp_name))
                self.assertIsInstance(getattr(elem1, '__{}'.format(exp_comp_name)), comp_cls,
                                      msg='Bad component type for name {!r}'.format(exp_comp_name))
                self.assertTrue(hasattr(elem1, actual_comp_name.priv_name),
                                msg='No component with name {!r}'.format(exp_comp_name))
                self.assertIsInstance(getattr(elem1, actual_comp_name.priv_name), comp_cls,
                                      msg='Bad component type for name {!r}'.format(exp_comp_name))
                self.assertEqual(comp_name, actual_comp_name.xml_name[1],
                                      msg='Bad component XML name for name {!r}'.format(exp_comp_name))
        else:
            elem_cls0 = type('Element0', (base_elem_cls,), {comp_name: comp_cls()})

    @parameterized.expand(((cls,) for cls in [
        BaseNSComponent,
        partial(NSComponentName, name='name'),
        ElementAttribute,
        Element,
        FeedItem,
        RssItem,
        predefined_items.NSItem4,
        predefined_items.NSItemFullNested,
        type('DerivedElement', (Element,), {}),
        partial(MultipleElements, base_element_cls=Element),
    ]), name_func=full_name_func)
    def test_settings_immutability(self, comp_cls):
        comp = comp_cls()
        settings1 = comp.settings
        settings2 = comp.settings
        self.assertEqual(settings1, settings2)
        self.assertIsNot(settings1, settings2)
        settings2['bla'] = True
        self.assertNotEqual(settings1, settings2)

        new_comp = comp_cls(**settings1)
        settings3 = new_comp.settings
        self.assertEqual(settings1, settings3)
        self.assertIsNot(settings1, settings3)


    @parameterized.expand((
        (comp_cls, first_args, second_args)
        for comp_cls, args in [
            (BaseNSComponent, [{'ns_prefix': '', 'ns_uri': ''}, {'ns_prefix': 'prefix', 'ns_uri': 'id'}]),
            (NSComponentName, [{'name': name, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                               for name, ns in product(['name 1', 'name 2'],
                                                       [('', ''), ('prefix', 'id')])]),
            (ElementAttribute, [{'required': r, 'is_content': c, 'serializer': s,
                                 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                                for r, c, s, ns in product([True, False], [True, False], [str, format_rfc822],
                                                           [('', ''), ('prefix', 'id')])
                                if not (c and ns[1])]),
            (Element, [{'required': r, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                       for r, ns in product([True, False], [('', ''), ('prefix', 'id')])]),
            (FeedItem, [{'required': r, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                        for r, ns in product([True, False], [('', ''), ('prefix', 'id')])]),
            (RssItem, [{'required': r, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                       for r, ns in product([True, False], [('', ''), ('prefix', 'id')])]),
            (predefined_items.NSItem4, [{'required': r, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                                        for r, ns in product([True, False], [('', ''), ('prefix', 'id')])]),
            (predefined_items.NSItemFullNested, [{'required': r, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                                                 for r, ns in product([True, False], [('', ''), ('prefix', 'id')])]),
            (type('DerivedElement', (Element,), {}), [{'required': r, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                                                      for r, ns in product([True, False], [('', ''), ('prefix', 'id')])]),
            (MultipleElements, [{'required': r, 'base_element_cls': b, 'ns_prefix': ns[0], 'ns_uri': ns[1]}
                                for r, b, ns in product([True, False],
                                                        [Element, predefined_items.NSElement4],
                                                        [('', ''), ('prefix', 'id')])]),
        ]
        for first_args, second_args in combinations_with_replacement(args, 2)
    ), name_func=full_name_func)
    def test_components_compatibility(self, comp_cls, first_args, second_args):
        first_comp = comp_cls(**first_args)
        second_comp = comp_cls(**second_args)
        assert_bool = getattr(self, 'assertTrue' if first_args == second_args else 'assertFalse')
        assert_bool(first_comp.compatible_with(second_comp))
        assert_bool(second_comp.compatible_with(first_comp))

    @parameterized.expand(chain(
        ((elem1_name,
          elem2.__class__,
          elem1_name == elem2_name,
          'Could not assign value')
         for (elem1_name, elem1), (elem2_name, elem2) in product(RssItem().elements.items(),
                                                                 RssItem().elements.items())
         if not isinstance(elem1, MultipleElements) and not isinstance(elem2, MultipleElements)),
        ((elem_name,
          partial(elem.__class__, **{'required': required, 'ns_prefix': ns[0], 'ns_uri': ns[1]}),
          elem.required == required and elem.ns_prefix == ns[0] and elem.ns_uri == ns[1],
          'incompatible')
         for (elem_name, elem) in RssItem().elements.items()
         if not isinstance(elem, MultipleElements)
         for required, ns in product([True, False], [('', ''), ('prefix', 'id')]))
    ), name_func=full_name_func)
    def test_element_assignment_compatibility(self, elem_name, new_elem_cls, compatible, msg):
        item = RssItem()
        elem2 = new_elem_cls()
        if compatible:
            setattr(item, str(elem_name), elem2)
            self.assertIs(elem2, getattr(item, str(elem_name)))
            self.assertIs(elem2, item.elements[elem_name])
            self.assertIs(elem2, item.children[elem_name])
        else:
            with six.assertRaisesRegex(self, InvalidElementValueError, msg):
                setattr(item, str(elem_name), elem2)


if __name__ == "__main__":
    unittest.main()
