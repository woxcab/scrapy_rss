# -*- coding: utf-8 -*-

import unittest
from itertools import product
from parameterized import parameterized
import scrapy
import six
from scrapy_rss import FeedItem, RssItem, RssedItem
from scrapy_rss.rss.old.items import RssedItem as OldRssedItem
from tests.utils import RssTestCase, full_name_func


class MyItem1(FeedItem):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.rss = RssItem()


class MyItem2(FeedItem):
    field = scrapy.Field()
    field2 = scrapy.Field()

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.rss = RssItem()


class MyItem3(RssedItem):
    pass


class MyItem4(RssedItem):
    field = scrapy.Field()
    field2 = scrapy.Field()


class MyItem5(OldRssedItem):
    pass


class MyItem6(OldRssedItem):
    field = scrapy.Field()
    field2 = scrapy.Field()


class TestFeedItem(RssTestCase):
    def test_feed_item(self):
        from scrapy_rss import FeedItem as FeedItem1
        from scrapy_rss.meta import FeedItem as FeedItem2
        from scrapy_rss.meta.item import FeedItem as FeedItem3

        self.assertIs(FeedItem1, FeedItem)
        self.assertIs(FeedItem2, FeedItem)
        self.assertIs(FeedItem3, FeedItem)

    @parameterized.expand(((item_cls,) for item_cls in (MyItem2, MyItem4, MyItem6)),
                          name_func=full_name_func)
    def test_field_init(self, item_cls):
        data = {'field': 'value1', 'field2': 2}
        item = item_cls(**data)
        for key, value in data.items():
            self.assertEqual(item[key], value)

    def test_dict_init(self):
        d = {'field': 'value1', 'field2': 2}
        item = MyItem4(d)
        for key, value in d.items():
            self.assertEqual(item[key], value)

    @parameterized.expand((
        (key, value, item_cls)
        for (key, value), item_cls in product([
            ('bad_key', 1),
            ('elements', 'nothing')
        ], [
            MyItem1, MyItem2, MyItem3, MyItem4, MyItem5, MyItem6
        ])
    ), name_func=full_name_func)
    def test_bad_dict_init(self, key, value, item_cls):
        with six.assertRaisesRegex(self, KeyError, r'does not support components: '):
            item_cls(**{key: value})

    @parameterized.expand(((item_cls,) for item_cls in (MyItem2, MyItem4, MyItem6)),
                          name_func=full_name_func)
    def test_field_setter(self, item_cls):
        item = item_cls()
        item['field'] = 'value'
        item.rss = None
        item.new_attr = 'OK'

    @parameterized.expand(((item_cls,) for item_cls in (MyItem2, MyItem4, MyItem6)),
                          name_func=full_name_func)
    def test_bad_field_setter(self, item_cls):
        item = item_cls()
        with six.assertRaisesRegex(self, AttributeError,  r'Use item\[[^\]]+\] = .*? to set field value',
                                   msg="Allowed assignment to Scrapy fields [{} class]"
                                       .format(item.__class__.__name__)):
            item.field = None
        with six.assertRaisesRegex(self, KeyError, r'does not support field:'):
            item['unknown_field'] = 'Bad'

    @parameterized.expand(((item_cls,) for item_cls in (MyItem2, MyItem4, MyItem6)),
                          name_func=full_name_func)
    def test_field_getter(self, item_cls):
        item = item_cls()
        with six.assertRaisesRegex(self, AttributeError, r'Use item\[[^\]]+\] to get field value'):
            _ = item.field
        _ = item.rss

        item.new_attr = None
        _ = item.new_attr

    @parameterized.expand(((item_cls,)
                           for item_cls in (MyItem1, MyItem2, MyItem3, MyItem4, MyItem5, MyItem6)),
                          name_func=full_name_func)
    def test_uniqueness(self, item_cls):
        item11 = item_cls()
        item12 = item_cls()
        self.assertNotEqual(id(item11.rss), id(item12.rss),
                            msg='[{} class]'.format(item_cls.__name__))

    def test_inheritance(self):
        class Derived1(FeedItem):
            pass

        Derived1()

        class Derived2(FeedItem):
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
