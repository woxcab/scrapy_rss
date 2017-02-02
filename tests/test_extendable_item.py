# -*- coding: utf-8 -*-

import unittest
import scrapy
from scrapy_rss import ExtendableItem, RssItem
from tests.utils import RssTestCase


class TestExtendableItem(RssTestCase):
    class MyItem1(ExtendableItem):
        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)
            self.rss = RssItem()

    class MyItem2(ExtendableItem):
        field = scrapy.Field()

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)
            self.rss = RssItem()

    def test_field_setter(self):
        item = self.MyItem2()
        with self.assertRaisesRegexp(AttributeError,  r'Use item\[[^\]]+\] = .*? to set field value',
                                     msg="Allowed assignment to Scrapy fields"):
            item.field = None
        item.rss = None
        item.new_attr = None

    def test_field_getter(self):
        item = self.MyItem2()
        with self.assertRaisesRegexp(AttributeError, r'Use item\[[^\]]+\] to get field value'):
            _ = item.field
        _ = item.rss

        item.new_attr = None
        _ = item.new_attr

    def test_uniqueness(self):
        item11 = self.MyItem1()
        item12 = self.MyItem1()
        self.assertNotEqual(id(item11.rss), id(item12.rss))

        item21 = self.MyItem2()
        item22 = self.MyItem2()
        self.assertNotEqual(id(item21.rss), id(item22.rss))


if __name__ == '__main__':
    unittest.main()
