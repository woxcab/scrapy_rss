# -*- coding: utf-8 -*-

import unittest
import scrapy
from scrapy_rss import ExtendableItem, RssItem, RssedItem
from tests.utils import RssTestCase


class TestExtendableItem(RssTestCase):
    class MyItem1(ExtendableItem):
        def __init__(self, **kwargs):
            super(self.__class__, self).__init__(**kwargs)
            self.rss = RssItem()

    class MyItem2(ExtendableItem):
        field = scrapy.Field()

        def __init__(self, **kwargs):
            super(self.__class__, self).__init__(**kwargs)
            self.rss = RssItem()

    class MyItem3(RssedItem):
        pass

    class MyItem4(RssedItem):
        field = scrapy.Field()

    def test_field_init(self):
        value = 'value'
        for item_cls in (self.MyItem2, self.MyItem4):
            item = item_cls(field=value)
            self.assertEqual(item['field'], value)

    def test_field_setter(self):
        for item in (self.MyItem2(), self.MyItem4()):
            with self.assertRaisesRegexp(AttributeError,  r'Use item\[[^\]]+\] = .*? to set field value',
                                         msg="Allowed assignment to Scrapy fields [{} class]"
                                             .format(item.__class__.__name__)):
                item.field = None
            item.rss = None
            item.new_attr = None

    def test_field_getter(self):
        for item in (self.MyItem2(), self.MyItem4()):
            with self.assertRaisesRegexp(AttributeError, r'Use item\[[^\]]+\] to get field value'):
                _ = item.field
            _ = item.rss

            item.new_attr = None
            _ = item.new_attr

    def test_uniqueness(self):
        for item_cls in (self.MyItem1, self.MyItem2, self.MyItem3, self.MyItem4):
            item11 = item_cls()
            item12 = item_cls()
            self.assertNotEqual(id(item11.rss), id(item12.rss),
                                msg='[{} class]'.format(item_cls.__name__))

    def test_inheritance(self):
        class Derived1(ExtendableItem):
            pass

        Derived1()

        class Derived2(ExtendableItem):
            def __init__(self, **kwargs):
                super(Derived2, self).__init__(**kwargs)

        Derived2()

        class Derived3(RssedItem):
            pass

        Derived3()

        class Derived4(RssedItem):
            def __init__(self, **kwargs):
                super(Derived4, self).__init__(**kwargs)

        Derived4()


if __name__ == '__main__':
    unittest.main()
