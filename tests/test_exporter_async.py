# -*- coding: utf-8 -*-
from packaging.version import Version
import sys
import os
import re
from itertools import chain, combinations
from functools import partial

from parameterized import parameterized
from lxml import etree

import scrapy
from scrapy.item import Item as BaseItem
from scrapy.exceptions import NotConfigured, CloseSpider

from scrapy_rss.items import RssItem, FeedItem
from scrapy_rss.rss.old.items import RssItem as OldRssItem
from scrapy_rss.meta import Element, ElementAttribute
from scrapy_rss.exceptions import *
from scrapy_rss.exporters import FeedItemExporter, RssItemExporter

import pytest
from tests import predefined_items
from tests.utils import RssTestCase, full_name_func
from tests.exporter_utils import CrawlerContext, default_feed_settings, FeedSettings, FullRssItemExporter


if Version(scrapy.__version__) >= Version('2.14'):
    import asyncio
    import twisted
    from twisted.internet.asyncioreactor import AsyncioSelectorReactor
    from unittest import IsolatedAsyncioTestCase

    initialized_items = predefined_items.PredefinedItems()
    NSItem0 = predefined_items.NSItem0
    NSItem1 = predefined_items.NSItem1
    NSItem2 = predefined_items.NSItem2
    NSItem3 = predefined_items.NSItem3


    class TestExporting(IsolatedAsyncioTestCase, RssTestCase):
        async def asyncSetUp(self):
            await super().asyncSetUp()
            self._orig_reactor_mod = sys.modules.get("twisted.internet.reactor")
            self._orig_reactor_attr = getattr(twisted.internet, "reactor", None)

            loop = asyncio.get_running_loop()
            asyncio_reactor = AsyncioSelectorReactor(eventloop=loop)

            sys.modules["twisted.internet.reactor"] = asyncio_reactor
            twisted.internet.reactor = asyncio_reactor

        async def asyncTearDown(self):
            if self._orig_reactor_mod is None:
                sys.modules.pop("twisted.internet.reactor", None)
            else:
                sys.modules["twisted.internet.reactor"] = self._orig_reactor_mod

            if self._orig_reactor_attr is None:
                if hasattr(twisted.internet, "reactor"):
                    delattr(twisted.internet, "reactor")
            else:
                twisted.internet.reactor = self._orig_reactor_attr

            await super().asyncTearDown()

        @parameterized.expand(zip(chain.from_iterable(
            combinations(default_feed_settings.items(), r)
            for r in range(1, len(default_feed_settings)))))
        def test_partial_required_settings(self, partial_settings):
            with FeedSettings() as feed_settings:
                partial_settings = dict(partial_settings)
                if 'feed_file' in partial_settings:
                    partial_settings['feed_file'] = feed_settings['feed_file']
                undefined_settings = [name.upper()
                                      for name in set(default_feed_settings) - set(partial_settings)]
                with six.assertRaisesRegex(self, NotConfigured,
                                           '({})'.format('|'.join(undefined_settings))
                                                if len(undefined_settings) > 1 else undefined_settings[0],
                                           msg='The feed file, title, link and description must be specified, but the absence of {} is allowed'
                                                 .format(undefined_settings)):
                    with CrawlerContext(**partial_settings):
                        pass

        def test_empty_feed(self):
            with self.assertRaises(CloseSpider):
                feed_settings = dict(default_feed_settings)
                feed_settings['feed_file'] = 'non/existent/filepath'
                with CrawlerContext(**feed_settings):
                    pass

            with FeedSettings() as feed_settings:
                with CrawlerContext(**feed_settings):
                    pass

                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'empty_feed.rss')) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read())

        def test_custom_exporter1(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                crawler_settings['FEED_EXPORTER'] = 'tests.exporter_utils.FullRssItemExporter'

                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                    pass
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', 'full_empty_feed.rss')) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read(),
                                                             excepted_elements=None)

        def test_custom_exporter2(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                crawler_settings['FEED_EXPORTER'] = FullRssItemExporter
                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                    pass
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', 'full_empty_feed.rss')) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read(),
                                                             excepted_elements=None)

        def test_custom_exporter3(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                class InvalidRssItemExporter1(FeedItemExporter):
                    def __init__(self, file, channel_title, channel_link, channel_description,
                                 managing_editor='Manager Name',
                                 *args, **kwargs):
                        super(InvalidRssItemExporter1, self) \
                            .__init__(file, channel_title, channel_link, channel_description,
                                      managing_editor=managing_editor, *args, **kwargs)

                crawler_settings['FEED_EXPORTER'] = InvalidRssItemExporter1
                with six.assertRaisesRegex(self, ValueError, 'managingEditor'):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                        pass

        def test_custom_exporter4(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                class InvalidRssItemExporter2(FeedItemExporter):
                    def __init__(self, file, channel_title, channel_link, channel_description,
                                 webmaster='Webmaster Name',
                                 *args, **kwargs):
                        super(InvalidRssItemExporter2, self) \
                            .__init__(file, channel_title, channel_link, channel_description,
                                      webmaster=webmaster, *args, **kwargs)

                crawler_settings['FEED_EXPORTER'] = InvalidRssItemExporter2
                with six.assertRaisesRegex(self, ValueError, 'webMaster'):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                        pass

        def test_custom_exporter5(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                class MultipleCategoriesRssItemExporter(FeedItemExporter):
                    def __init__(self, file, channel_title, channel_link, channel_description,
                                 category=('category 1', 'category 2'),
                                 *args, **kwargs):
                        super(MultipleCategoriesRssItemExporter, self) \
                            .__init__(file, channel_title, channel_link, channel_description,
                                      category=category, *args, **kwargs)

                crawler_settings['FEED_EXPORTER'] = MultipleCategoriesRssItemExporter
                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                    pass
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', 'empty_feed_with_categories.rss')) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read())

        def test_custom_exporter6(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                class NoGeneratorRssItemExporter(FeedItemExporter):
                    def __init__(self, file, channel_title, channel_link, channel_description,
                                 generator=None,
                                 *args, **kwargs):
                        super(NoGeneratorRssItemExporter, self) \
                            .__init__(file, channel_title, channel_link, channel_description,
                                      generator=generator, *args, **kwargs)

                crawler_settings['FEED_EXPORTER'] = NoGeneratorRssItemExporter
                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                    pass
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'empty_feed_without_generator.rss')) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read(), excepted_elements='lastBuildDate')

        def test_custom_exporter7(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                class NoGeneratorRssItemExporter2(RssItemExporter):
                    def __init__(self, file, channel_title, channel_link, channel_description,
                                 generator=None,
                                 *args, **kwargs):
                        super(NoGeneratorRssItemExporter2, self) \
                            .__init__(file, channel_title, channel_link, channel_description,
                                      generator=generator, *args, **kwargs)

                crawler_settings['FEED_EXPORTER'] = NoGeneratorRssItemExporter2
                with pytest.warns(DeprecationWarning, match='Use FeedItemExporter instead'):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                        pass
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'empty_feed_without_generator.rss')) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read(), excepted_elements='lastBuildDate')

        def test_custom_exporter8(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                class InvalidExporter(object):
                    pass

                crawler_settings['FEED_EXPORTER'] = InvalidExporter
                with six.assertRaisesRegex(self, TypeError, 'FEED_EXPORTER'):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                        pass

        def test_custom_exporter9(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                class BadRssItemExporter(FeedItemExporter):
                    def __init__(self, *args, **kwargs):
                        super(BadRssItemExporter, self).__init__(*args, **kwargs)
                        self.channel = scrapy.Item()

                crawler_settings['FEED_EXPORTER'] = BadRssItemExporter
                with six.assertRaisesRegex(self, ValueError, 'Argument element must be instance of <Element>'):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                        pass

        async def test_deprecated_pipeline(self):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                item = initialized_items.items['full_rss_item']
                crawler_settings['ITEM_PIPELINES'] = {'scrapy_rss.pipelines.RssExportPipeline': 900}
                with pytest.warns(DeprecationWarning, match='Use FeedExportPipeline instead'):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings) as context:
                        await context.ipm.process_item_async(item)
                with open(feed_settings['feed_file']) as data, \
                        open(os.path.join(os.path.dirname(__file__),
                                          'expected_rss', 'full_rss_item.rss')) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())


        @parameterized.expand(((item_cls,) for item_cls in [RssItem, OldRssItem]),
                              name_func=full_name_func)
        async def test_item_validation1(self, item_cls):
            item = item_cls()
            with FeedSettings() as feed_settings:
                with six.assertRaisesRegex(self, InvalidFeedItemComponentsError,
                                           r'Missing or invalid one or more required components'):
                    with CrawlerContext(**feed_settings) as context:
                        await context.ipm.process_item_async(item)

                item.title = 'Title'
                item.validate()
                self.assertTrue(item.is_valid())
                with CrawlerContext(**feed_settings) as context:
                    await context.ipm.process_item_async(item)

                item.enclosure.url = 'http://example.com/content'
                with six.assertRaisesRegex(self, InvalidFeedItemComponentsError,
                                           r'Missing or invalid one or more required components'):
                    with CrawlerContext(**feed_settings) as context:
                        await context.ipm.process_item_async(item)



        async def test_item_validation2(self):
            class NonStandardElement(Element):
                first_attribute = ElementAttribute(required=True, is_content=True)
                second_attribute = ElementAttribute(required=True)

            class NonStandardItem(RssItem):
                element = NonStandardElement()

            with FeedSettings() as feed_settings:
                item = NonStandardItem(title='Title')
                item.validate()
                self.assertTrue(item.is_valid())
                with CrawlerContext(**feed_settings) as context:
                    await context.ipm.process_item_async(item)

                with six.assertRaisesRegex(self, InvalidElementValueError, 'Could not assign'):
                    item.element = 'valid value'

                item.element.first_attribute = 'valid value'
                with six.assertRaisesRegex(self, InvalidFeedItemComponentsError,
                                           r'Missing or invalid one or more required components'):
                    with CrawlerContext(**feed_settings) as context:
                        await context.ipm.process_item_async(item)

        async def test_item_validation3(self):
            class InvalidSuperItem1(FeedItem):
                pass

            class InvalidSuperItem2(FeedItem):
                field = scrapy.Field()

            class InvalidSuperItem3(FeedItem):
                rss = scrapy.Field()

            with FeedSettings() as feed_settings:
                for invalid_item_cls in (InvalidSuperItem1, InvalidSuperItem2, InvalidSuperItem3):
                    with six.assertRaisesRegex(self, InvalidFeedItemError, "Item.*? type 'RssItem'",
                                               msg=str(invalid_item_cls)):
                        with CrawlerContext(**feed_settings) as context:
                            await context.ipm.process_item_async(invalid_item_cls())


        async def test_item_validation4(self):
            class Element0(Element):
                attr = ElementAttribute()

            class Item10(RssItem):
                req_attr = ElementAttribute(required=True)

            ValidItem10 = partial(Item10, {'req_attr': 0})


            class Element10(Element):
                attr = ElementAttribute()
                req_attr = ElementAttribute(required=True)

            class Item11(RssItem):
                elem = Element10()

            InvalidItem11 = partial(Item11, {'elem': {'attr': 1}})
            ValidItem11 = partial(Item11, {'elem': {'req_attr': True}})


            class Item20(RssItem):
                req_elem = Element(required=True)


            class Element20(Element):
                attr = ElementAttribute()
                req_elem = Element0(required=True)

            class Item21(RssItem):
                elem = Element20()

            InvalidItem21 = partial(Item21, {'elem': {'attr': 1}})
            ValidItem21 = partial(Item21, {'elem': {'attr': 1, 'req_elem': {'attr': 'value'}}})


            class Item3(RssItem):
                req_attr = ElementAttribute(required=True)
                req_elem = Element(required=True)


            with FeedSettings() as feed_settings:
                for item_cls in (Item10, InvalidItem11, Item20, InvalidItem21, Item3):
                    with six.assertRaisesRegex(self, InvalidFeedItemComponentsError,
                                               "Missing or invalid one or more required components",
                                               msg=str(item_cls)):
                        with CrawlerContext(**feed_settings) as context:
                            await context.ipm.process_item_async(item_cls(title='Title'))
                for item_cls in (ValidItem10, Item11, ValidItem11, Item21, ValidItem21):
                    item = item_cls(title='Title')
                    item.validate()
                    self.assertTrue(item.is_valid())
                    with CrawlerContext(**feed_settings) as context:
                        await context.ipm.process_item_async(item)

        def test_item_validation5(self):
            class Element0(Element):
                attr = ElementAttribute()

            class Element1(Element):
                attr0 = ElementAttribute()
                elem0 = Element0(required=True)

            class Element2(Element):
                elem1 = Element1()

            class Item0(RssItem):
                elem2 = Element2()

            item1 = Item0()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'title' component value:.*? title or description must be present"):
                item1.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.title' component value:.*? title or description must be present"):
                item1.validate('item')
            self.assertFalse(item1.is_valid())

            item1.description = 'Description'
            item1.validate()
            self.assertTrue(item1.is_valid())
            item1.elem2.elem1.attr0 = 'value'
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'elem2.elem1.elem0' component value"):
                item1.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.elem2.elem1.elem0' component value"):
                item1.validate('item')
            self.assertFalse(item1.is_valid())
            item1.elem2.elem1.elem0.attr = 5
            item1.validate()
            self.assertTrue(item1.is_valid())

            item2 = Item0({'title': 'Title', 'elem2': {'elem1': {'attr0': -5}}})
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'elem2.elem1.elem0' component value"):
                item2.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.elem2.elem1.elem0' component value"):
                item2.validate('item')
            self.assertFalse(item2.is_valid())

            item3 = Item0({'title': 'Title', 'elem2': {'elem1': {'elem0': {'attr': 0}}}})
            item3.validate()
            self.assertTrue(item3.is_valid())

            item3.elem2.elem1._ns_prefix = 'prefix'
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'elem2.elem1' component value.*? no namespace URI"):
                item3.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.elem2.elem1' component value.*? no namespace URI"):
                item3.validate('item')
            item3.elem2.elem1.ns_uri = 'id'
            item3.validate()
            item3.validate('item')
            self.assertTrue(item3.is_valid())


        def test_item_validation6(self):
            class Element1(Element):
                attr1 = ElementAttribute()
                attr2 = ElementAttribute(required=True)

            class Element2(Element):
                elem1 = Element1()

            class Item1(RssItem):
                elem2 = Element2()

            item4 = Item1()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'title' component value:.*? title or description must be present"):
                item4.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.title' component value:.*? title or description must be present"):
                item4.validate('item')
            self.assertFalse(item4.is_valid())
            item4.description = 'Description'
            item4.validate()
            self.assertTrue(item4.is_valid())
            item4.elem2.elem1.attr1 = 'value'
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'elem2.elem1.attr2' component value"):
                item4.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.elem2.elem1.attr2' component value"):
                item4.validate('item')
            self.assertFalse(item4.is_valid())
            item4.elem2.elem1.attr2 = False
            item4.validate()
            self.assertTrue(item4.is_valid())

            item5 = Item1({'description': 'Description', 'elem2': {'elem1': {'attr1': -5}}})
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'elem2.elem1.attr2' component value"):
                item5.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.elem2.elem1.attr2' component value"):
                item5.validate('item')
            self.assertFalse(item5.is_valid())

            item6 = Item1({'description': 'Description', 'elem2': {'elem1': {'attr2': -5}}})
            item6.validate()
            self.assertTrue(item6.is_valid())

            item6.elem2._ns_prefix = 'prefix'
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'elem2' component value.*? no namespace URI"):
                item6.validate()
            with six.assertRaisesRegex(self, InvalidComponentError,
                                       "Invalid 'item.elem2' component value.*? no namespace URI"):
                item6.validate('item')
            self.assertFalse(item6.is_valid())
            item6.elem2.ns_uri = 'id'
            item6.validate()
            item6.validate('item')
            self.assertTrue(item6.is_valid())

        @parameterized.expand([
            (RssItem(title='Title 1', pubDate='Invalid date'),
             r"time data.* does not match format"),
            (RssItem(title='Title 2', pubDate='Fri, 01 Dec 2000 23:59:60 +0400'),
             r"second must be in 0..59"),
        ])
        async def test_item_attr_serialization(self, item, exc_msg_match):
            with FeedSettings() as feed_settings:
                with six.assertRaisesRegex(self, InvalidFeedItemComponentsError, exc_msg_match):
                    with CrawlerContext(**feed_settings) as context:
                        await context.ipm.process_item_async(item)

        @parameterized.expand([
            ('Invalid date string', r"time data.* does not match format"),
            ('Fri, 01 Dec 2000 23:60:59 +0400', r"time data.* does not match format"),
            ('Fri, 01 Dec 2000 23:59:60 +0400', r"second must be in 0..59"),
        ])
        def test_channel_attr_serialization(self, date_str, exc_msg_match):
            class BadRssItemExporter(FeedItemExporter):
                def __init__(self, file, channel_title, channel_link, channel_description,
                             pubdate=date_str,
                             *args, **kwargs):
                    super(BadRssItemExporter, self) \
                        .__init__(file, channel_title, channel_link, channel_description,
                                  pubdate=pubdate,
                                  *args, **kwargs)

            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                crawler_settings['FEED_EXPORTER'] = BadRssItemExporter
                with six.assertRaisesRegex(self, InvalidFeedItemComponentsError, exc_msg_match):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                        pass

        @parameterized.expand(zip([scrapy.Item, BaseItem, dict]))
        def test_bad_item_cls(self, item_cls):
            with FeedSettings() as feed_settings:
                crawler_settings = dict(CrawlerContext.default_settings)
                crawler_settings['FEED_ITEM_CLASS'] = item_cls

                with six.assertRaisesRegex(self, ValueError, 'must be strict subclass of FeedItem'):
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                        pass

        @parameterized.expand(initialized_items.items.items())
        async def test_single_item_in_the_feed(self, item_name, item):
            with FeedSettings() as feed_settings:
                class SuperItem(FeedItem):
                    some_field = scrapy.Field()

                    def __init__(self):
                        super(SuperItem, self).__init__()
                        self.rss = RssItem()

                super_item = SuperItem()
                super_item.rss = item

                for current_item in (item, super_item):
                    with CrawlerContext(**feed_settings) as context:
                        await context.ipm.process_item_async(current_item)
                    with open(feed_settings['feed_file']) as data, \
                         open(os.path.join(os.path.dirname(__file__),
                                           'expected_rss', '{}.rss'.format(item_name))) as expected:
                        self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

        @parameterized.expand(initialized_items.ns_items)
        async def test_single_ns_item_in_the_feed(self, item_name, namespaces, item_cls, item):
            with FeedSettings() as feed_settings:
                class SuperItem(FeedItem):
                    some_field = scrapy.Field()

                    def __init__(self):
                        super(SuperItem, self).__init__()
                        self.rss = RssItem()

                crawler_settings = dict(CrawlerContext.default_settings)
                if namespaces is not None:
                    crawler_settings['FEED_NAMESPACES'] = namespaces
                if item_cls is not None:
                    crawler_settings['FEED_ITEM_CLASS'] = item_cls

                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings) as context:
                    await context.ipm.process_item_async(item)
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', '{}.rss'.format(item_name))) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

                super_item = SuperItem()
                super_item.rss = item
                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings) as context:
                    await context.ipm.process_item_async(super_item)
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', '{}.rss'.format(item_name))) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

        async def test_all_items_in_the_single_feed(self):
            copy_raw_text_for_items = {'full_nested_item'}
            raw_items_text = ''
            with FeedSettings() as feed_settings:
                with open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', 'empty_feed.rss'), 'rb') as feed_f:
                    feed_tree = etree.fromstring(feed_f.read())
                    feed_channel = feed_tree.xpath('//channel')[0]
                    with CrawlerContext(**feed_settings) as context:
                        for item_name, item in initialized_items.items.items():
                            await context.ipm.process_item_async(item)
                            with open(os.path.join(os.path.dirname(__file__),
                                                   'expected_rss', '{}.rss'.format(item_name)), 'rb') as item_f:
                                if item_name in copy_raw_text_for_items:
                                    match = re.search(r'<item.*</item>',
                                                       item_f.read().decode('utf-8'),
                                                       flags=re.S)
                                    raw_items_text += match.group(0) + '\n'
                                else:
                                    item_tree = etree.fromstring(item_f.read())
                                    feed_channel.extend(item_tree.xpath('//item'))
                    expected = etree.tostring(feed_tree, encoding='utf-8').decode('utf-8')
                    expected = expected.replace('</channel>', raw_items_text + '\n</channel>')
                    with open(feed_settings['feed_file']) as data:
                        self.assertUnorderedXmlEquivalentOutputs(data.read(), expected)

        async def test_ns_items_in_the_single_feed(self):
            with FeedSettings() as feed_settings:
                base_filename, item_cls, _ = initialized_items.ns_items_of_same_cls[0]
                with open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', '{}.rss'.format(base_filename)), 'rb') as feed_f:
                    feed_tree = etree.fromstring(feed_f.read())
                    feed_channel = feed_tree.xpath('//channel')[0]
                    for item in list(feed_channel.xpath('./item')):
                        feed_channel.remove(item)
                    crawler_settings = dict(CrawlerContext.default_settings)
                    crawler_settings['FEED_ITEM_CLS'] = item_cls
                    with CrawlerContext(crawler_settings=crawler_settings, **feed_settings) as context:
                        for item_name, item_cls, item in initialized_items.ns_items_of_same_cls:
                            await context.ipm.process_item_async(item)
                            with open(os.path.join(os.path.dirname(__file__),
                                                   'expected_rss', '{}.rss'.format(item_name)), 'rb') as item_f:
                                item_tree = etree.fromstring(item_f.read())
                                feed_channel.extend(item_tree.xpath('//item'))
                    with open(feed_settings['feed_file']) as data:
                        self.assertUnorderedXmlEquivalentOutputs(data.read(), feed_tree)


if __name__ == '__main__':
    pytest.main()

