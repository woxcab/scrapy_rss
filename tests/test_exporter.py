# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
from itertools import chain, combinations
from functools import partial

from scrapy_rss.rss import channel_elements

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
from parameterized import parameterized
import six
from lxml import etree
from packaging.version import Version

import scrapy
from scrapy import signals
try:
    from scrapy.item import BaseItem
except ImportError:
    from scrapy.item import Item as BaseItem
from tests.utils import RaisedItemPipelineManager, full_name_func
from scrapy.exceptions import NotConfigured, CloseSpider
from scrapy.utils.misc import load_object
from scrapy.utils.test import get_crawler

from scrapy_rss.items import RssItem, FeedItem
from scrapy_rss.rss.old.items import RssItem as OldRssItem
from scrapy_rss.meta import Element, ElementAttribute
from scrapy_rss.exceptions import *
from scrapy_rss.exporters import FeedItemExporter, RssItemExporter
from scrapy_rss.utils import get_tzlocal

import pytest
from tests import predefined_items
from tests.utils import RssTestCase, FrozenDict

if Version(scrapy.__version__) >= Version('2.13'):
    from twisted.internet import reactor # not used but it's required

if six.PY2:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')


class CrawlerContext(object):
    default_settings = FrozenDict({'ITEM_PIPELINES':
                                       {'scrapy_rss.pipelines.FeedExportPipeline': 900,},
                                   'LOG_LEVEL': 'WARNING',
                                   'EXTENSIONS': {
                                       'scrapy.extensions.memusage.MemoryUsage': None,},
                                   })

    def __init__(self, feed_file=None, feed_title=None, feed_link=None, feed_description=None,
                 crawler_settings=None):
        settings = crawler_settings if crawler_settings else dict(self.default_settings)
        if feed_file:
            settings['FEED_FILE'] = feed_file
        if feed_title:
            settings['FEED_TITLE'] = feed_title
        if feed_link:
            settings['FEED_LINK'] = feed_link
        if feed_description:
            settings['FEED_DESCRIPTION'] = feed_description
        self.crawler = get_crawler(settings_dict=settings)
        self.spider = scrapy.Spider.from_crawler(self.crawler, 'example.com')
        self.spider.parse = lambda response: ()
        item_processor = settings.get('ITEM_PROCESSOR')
        if not item_processor:
            item_processor = RaisedItemPipelineManager
        elif isinstance(item_processor, six.string_types):
            item_processor = load_object(item_processor)

        self.ipm = item_processor.from_crawler(self.crawler)

    def __enter__(self):
        responses = self.crawler.signals.send_catch_log(signal=signals.spider_opened,
                                                        spider=self.spider)
        for _, failure in responses:
            if failure:
                failure.raiseException()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        responses = self.crawler.signals.send_catch_log(signal=signals.spider_closed,
                                                        spider=self.spider, reason=None)
        for _, failure in responses:
            if failure:
                failure.raiseException()


class FullRssItemExporter(FeedItemExporter):
    def __init__(self, file, channel_title, channel_link, channel_description,
                 language='en-US',
                 copyright='Data',
                 managing_editor='m@dot.com (Manager Name)',
                 webmaster='web@dot.com (Webmaster Name)',
                 pubdate=datetime(2000, 2, 1, 0, 10, 30, tzinfo=get_tzlocal()),
                 last_build_date=datetime(2000, 2, 1, 5, 10, 30, tzinfo=get_tzlocal()),
                 category='some category',
                 generator='tester',
                 docs='http://example.com/rss_docs',
                 cloud=FrozenDict({
                     'domain': 'rpc.sys.com',
                     'port': '80',
                     'path': '/RPC2',
                     'registerProcedure': 'myCloud.rssPleaseNotify',
                     'protocol': 'xml-rpc'
                 }),
                 ttl=60,
                 image=channel_elements.ImageElement(url='http://example.com/img.jpg',
                                                     width=54),
                 rating=4.0,
                 text_input=channel_elements.TextInputElement(title='Input title',
                                                              description='Description of input',
                                                              name='Input name',
                                                              link='http://example.com/cgi.py'),
                 skip_hours=(0, 1, 3, 7, 23),
                 skip_days=14,
                 *args, **kwargs):
        super(FullRssItemExporter, self) \
            .__init__(file, channel_title, channel_link, channel_description,
                      language=language, copyright=copyright, managing_editor=managing_editor,
                      webmaster=webmaster, pubdate=pubdate, last_build_date=last_build_date,
                      category=category, generator=generator,
                      docs=docs, cloud=cloud, ttl=ttl,
                      image=image, rating=rating, text_input=text_input,
                      skip_hours=skip_hours, skip_days=skip_days,
                      *args, **kwargs)


default_feed_settings = FrozenDict({'feed_file': 'feed.rss',
                                    'feed_title': 'Title',
                                    'feed_link': 'http://example.com/feed',
                                    'feed_description': 'Description'})


class FeedSettings(TemporaryDirectory):
    def __enter__(self):
        dirname = super(FeedSettings, self).__enter__()
        feed_settings = dict(default_feed_settings)
        feed_settings['feed_file'] = os.path.join(dirname, feed_settings['feed_file'])
        feed_settings = FrozenDict(feed_settings)
        return feed_settings


initialized_items = predefined_items.PredefinedItems()
NSItem0 = predefined_items.NSItem0
NSItem1 = predefined_items.NSItem1
NSItem2 = predefined_items.NSItem2
NSItem3 = predefined_items.NSItem3


class TestExporting(RssTestCase):
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
            crawler_settings['FEED_EXPORTER'] = 'tests.test_exporter.FullRssItemExporter'

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

    def test_deprecated_pipeline(self):
        with FeedSettings() as feed_settings:
            crawler_settings = dict(CrawlerContext.default_settings)
            item = initialized_items.items['full_rss_item']
            crawler_settings['ITEM_PIPELINES'] = {'scrapy_rss.pipelines.RssExportPipeline': 900}
            with pytest.warns(DeprecationWarning, match='Use FeedExportPipeline instead'):
                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings) as context:
                    context.ipm.process_item(item, context.spider)
            with open(feed_settings['feed_file']) as data, \
                    open(os.path.join(os.path.dirname(__file__),
                                      'expected_rss', 'full_rss_item.rss')) as expected:
                self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())


    @parameterized.expand(((item_cls,) for item_cls in [RssItem, OldRssItem]),
                          name_func=full_name_func)
    def test_item_validation1(self, item_cls):
        item = item_cls()
        with FeedSettings() as feed_settings:
            with six.assertRaisesRegex(self, InvalidFeedItemComponentsError,
                                       r'Missing one or more required components'):
                with CrawlerContext(**feed_settings) as context:
                    context.ipm.process_item(item, context.spider)

            item.title = 'Title'
            item.validate()
            self.assertTrue(item.is_valid())
            with CrawlerContext(**feed_settings) as context:
                context.ipm.process_item(item, context.spider)

            item.enclosure.url = 'http://example.com/content'
            with six.assertRaisesRegex(self, InvalidFeedItemComponentsError,
                                       r'Missing one or more required components'):
                with CrawlerContext(**feed_settings) as context:
                    context.ipm.process_item(item, context.spider)



    def test_item_validation2(self):
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
                context.ipm.process_item(item, context.spider)

            with six.assertRaisesRegex(self, InvalidElementValueError, 'Could not assign'):
                item.element = 'valid value'

            item.element.first_attribute = 'valid value'
            with six.assertRaisesRegex(self, InvalidFeedItemComponentsError,
                                       r'Missing one or more required components'):
                with CrawlerContext(**feed_settings) as context:
                    context.ipm.process_item(item, context.spider)

    def test_item_validation3(self):
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
                        context.ipm.process_item(invalid_item_cls(), context.spider)


    def test_item_validation4(self):
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
                                           "Missing one or more required components",
                                           msg=str(item_cls)):
                    with CrawlerContext(**feed_settings) as context:
                        context.ipm.process_item(item_cls(title='Title'), context.spider)
            for item_cls in (ValidItem10, Item11, ValidItem11, Item21, ValidItem21):
                item = item_cls(title='Title')
                item.validate()
                self.assertTrue(item.is_valid())
                with CrawlerContext(**feed_settings) as context:
                    context.ipm.process_item(item, context.spider)

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


    @parameterized.expand(zip([scrapy.Item, BaseItem, dict]))
    def test_bad_item_cls(self, item_cls):
        with FeedSettings() as feed_settings:
            crawler_settings = dict(CrawlerContext.default_settings)
            crawler_settings['FEED_ITEM_CLASS'] = item_cls

            with six.assertRaisesRegex(self, ValueError, 'must be strict subclass of FeedItem'):
                with CrawlerContext(crawler_settings=crawler_settings, **feed_settings):
                    pass

    @parameterized.expand(initialized_items.items.items())
    def test_single_item_in_the_feed(self, item_name, item):
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
                    context.ipm.process_item(current_item, context.spider)
                with open(feed_settings['feed_file']) as data, \
                     open(os.path.join(os.path.dirname(__file__),
                                       'expected_rss', '{}.rss'.format(item_name))) as expected:
                    self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

    @parameterized.expand(initialized_items.ns_items)
    def test_single_ns_item_in_the_feed(self, item_name, namespaces, item_cls, item):
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
                context.ipm.process_item(item, context.spider)
            with open(feed_settings['feed_file']) as data, \
                 open(os.path.join(os.path.dirname(__file__),
                                   'expected_rss', '{}.rss'.format(item_name))) as expected:
                self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

            super_item = SuperItem()
            super_item.rss = item
            with CrawlerContext(crawler_settings=crawler_settings, **feed_settings) as context:
                context.ipm.process_item(super_item, context.spider)
            with open(feed_settings['feed_file']) as data, \
                 open(os.path.join(os.path.dirname(__file__),
                                   'expected_rss', '{}.rss'.format(item_name))) as expected:
                self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

    def test_all_items_in_the_single_feed(self):
        copy_raw_text_for_items = {'full_nested_item'}
        raw_items_text = ''
        with FeedSettings() as feed_settings:
            with open(os.path.join(os.path.dirname(__file__),
                                   'expected_rss', 'empty_feed.rss'), 'rb') as feed_f:
                feed_tree = etree.fromstring(feed_f.read())
                feed_channel = feed_tree.xpath('//channel')[0]
                with CrawlerContext(**feed_settings) as context:
                    for item_name, item in initialized_items.items.items():
                        context.ipm.process_item(item, context.spider)
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

    def test_ns_items_in_the_single_feed(self):
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
                        context.ipm.process_item(item, context.spider)
                        with open(os.path.join(os.path.dirname(__file__),
                                               'expected_rss', '{}.rss'.format(item_name)), 'rb') as item_f:
                            item_tree = etree.fromstring(item_f.read())
                            feed_channel.extend(item_tree.xpath('//item'))
                with open(feed_settings['feed_file']) as data:
                    self.assertUnorderedXmlEquivalentOutputs(data.read(), feed_tree)


if __name__ == '__main__':
    pytest.main()

