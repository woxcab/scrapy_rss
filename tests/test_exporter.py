# -*- coding: utf-8 -*-

import itertools
import os
from datetime import datetime

import six
from frozendict import frozendict
from lxml import etree
import scrapy
from scrapy import signals
from tests.utils import RaisedItemPipelineManager
from scrapy.exceptions import NotConfigured, CloseSpider
from scrapy.utils.misc import load_object
from scrapy.utils.test import get_crawler
from scrapy.core.scraper import Scraper
from scrapy.crawler import Crawler

from scrapy_rss.items import RssItem, ExtendableItem, RssedItem
from scrapy_rss.meta import ItemElement, ItemElementAttribute
from scrapy_rss.exceptions import *
from scrapy_rss.exporters import RssItemExporter

import unittest
from tests.utils import RssTestCase


if six.PY2:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')


class CrawlerContext(object):
    default_settings = frozendict({'ITEM_PIPELINES':
                                       {'scrapy_rss.pipelines.RssExportPipeline': 900,},
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


class FullRssItemExporter(RssItemExporter):
    def __init__(self, file, channel_title, channel_link, channel_description,
                 language='en-US', copyright='Data', managing_editor='m@dot.com (Manager Name)',
                 webmaster='web@dot.com (Webmaster Name)',
                 pubdate=datetime(2000, 2, 1, 0, 10, 30), last_build_date=datetime(2000, 2, 1, 5, 10, 30),
                 category='some category', generator='tester',
                 docs='http://example.com/rss_docs', ttl=60,
                 *args, **kwargs):
        super(FullRssItemExporter, self) \
            .__init__(file, channel_title, channel_link, channel_description,
                      language=language, copyright=copyright, managing_editor=managing_editor,
                      webmaster=webmaster, pubdate=pubdate, last_build_date=last_build_date,
                      category=category, generator=generator,
                      docs=docs, ttl=ttl, *args, **kwargs)


class TestExporting(RssTestCase):
    feed_settings = frozendict({'feed_file': os.path.join(os.path.dirname(__file__), 'tmp', 'feed.rss'),
                                'feed_title': 'Title',
                                'feed_link': 'http://example.com/feed',
                                'feed_description': 'Description'})

    def __init__(self, *args, **kwargs):
        super(TestExporting, self).__init__(*args, **kwargs)

        minimal_item = RssItem()
        minimal_item.title = 'Title of minimal item'

        minimal_item2 = RssItem()
        minimal_item2.description = 'Description of minimal item'

        simple_item = RssItem()
        simple_item.title = 'Title of simple item'
        simple_item.description = 'Description of simple item'

        item_with_single_category = RssItem()
        item_with_single_category.title = 'Title of item with single category'
        item_with_single_category.category = 'Category 1'

        item_with_multiple_categories = RssItem()
        item_with_multiple_categories.title = 'Title of item with multiple categories'
        item_with_multiple_categories.category = ['Category 1', 'Category 2']

        item_with_guid = RssItem()
        item_with_guid.title = 'Title of item with guid'
        item_with_guid.guid = 'Identifier'

        item_with_unicode = RssItem()
        item_with_unicode.title = 'Title of item with unicode and special characters'
        item_with_unicode.description = "[Testing «ταБЬℓσ»: 1<2 & 4+1>3, now 20% off!]"

        item_with_enclosure = RssItem()
        item_with_enclosure.title = 'Title of item with enclosure'
        item_with_enclosure.enclosure.url = 'http://example.com/content'
        item_with_enclosure.enclosure.length = 0
        item_with_enclosure.enclosure.type = 'text/plain'

        self.items = {
                 'minimal_item': minimal_item,
                 'minimal_item2': minimal_item2,
                 'simple_item': simple_item,
                 'item_with_single_category': item_with_single_category,
                 'item_with_multiple_categories': item_with_multiple_categories,
                 'item_with_guid': item_with_guid,
                 'item_with_unicode': item_with_unicode,
                 'item_with_enclosure': item_with_enclosure,
                 }

    def test_empty_feed(self):
        for partial_settings in itertools.chain.from_iterable(
                itertools.combinations(self.feed_settings.items(), r)
                for r in range(1, len(self.feed_settings))):
            partial_settings = dict(partial_settings)
            undefined_settings = [name.upper() for name in set(self.feed_settings) - set(partial_settings)]
            with self.assertRaisesRegexp(NotConfigured,
                                         '({})'.format('|'.join(undefined_settings))
                                            if len(undefined_settings) > 1 else undefined_settings[0],
                                         msg='The feed file, title, link and description must be specified, but the absence of {} is allowed'
                                             .format(undefined_settings)):
                with CrawlerContext(**partial_settings):
                    pass

        with self.assertRaises(CloseSpider):
            feed_settings = dict(self.feed_settings)
            feed_settings['feed_file'] = 'non/existent/filepath'
            with CrawlerContext(**feed_settings):
                pass

        with CrawlerContext(**self.feed_settings):
            pass

        with open(self.feed_settings['feed_file']) as data, \
             open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'empty_feed.rss')) as expected:
            self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read())

    def test_custom_exporters(self):
        crawler_settings = dict(CrawlerContext.default_settings)
        crawler_settings['FEED_EXPORTER'] = 'tests.test_exporter.FullRssItemExporter'

        with CrawlerContext(crawler_settings=crawler_settings, **self.feed_settings):
            pass
        with open(self.feed_settings['feed_file']) as data, \
             open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'full_empty_feed.rss')) as expected:
            self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read(), excepted_elements=None)

        crawler_settings['FEED_EXPORTER'] = FullRssItemExporter
        with CrawlerContext(crawler_settings=crawler_settings, **self.feed_settings):
            pass
        with open(self.feed_settings['feed_file']) as data, \
             open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'full_empty_feed.rss')) as expected:
            self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read(), excepted_elements=None)

        class InvalidRssItemExporter1(RssItemExporter):
            def __init__(self, file, channel_title, channel_link, channel_description,
                         managing_editor='Manager Name',
                         *args, **kwargs):
                super(InvalidRssItemExporter1, self) \
                    .__init__(file, channel_title, channel_link, channel_description,
                              managing_editor=managing_editor, *args, **kwargs)

        crawler_settings['FEED_EXPORTER'] = InvalidRssItemExporter1
        with self.assertRaisesRegexp(ValueError, 'managing_editor'):
            with CrawlerContext(crawler_settings=crawler_settings, **self.feed_settings):
                pass

        class InvalidRssItemExporter2(RssItemExporter):
            def __init__(self, file, channel_title, channel_link, channel_description,
                         webmaster='Webmaster Name',
                         *args, **kwargs):
                super(InvalidRssItemExporter2, self) \
                    .__init__(file, channel_title, channel_link, channel_description,
                              webmaster=webmaster, *args, **kwargs)

        crawler_settings['FEED_EXPORTER'] = InvalidRssItemExporter2
        with self.assertRaisesRegexp(ValueError, 'webmaster'):
            with CrawlerContext(crawler_settings=crawler_settings, **self.feed_settings):
                pass

        class MultipleCategoriesRssItemExporter(RssItemExporter):
            def __init__(self, file, channel_title, channel_link, channel_description,
                         category=('category 1', 'category 2'),
                         *args, **kwargs):
                super(MultipleCategoriesRssItemExporter, self) \
                    .__init__(file, channel_title, channel_link, channel_description,
                              category=category, *args, **kwargs)

        crawler_settings['FEED_EXPORTER'] = MultipleCategoriesRssItemExporter
        with CrawlerContext(crawler_settings=crawler_settings, **self.feed_settings):
            pass
        with open(self.feed_settings['feed_file']) as data, \
             open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'empty_feed_with_categories.rss')) as expected:
            self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read())

        class NoGeneratorRssItemExporter(RssItemExporter):
            def __init__(self, file, channel_title, channel_link, channel_description,
                         generator='',
                         *args, **kwargs):
                super(NoGeneratorRssItemExporter, self) \
                    .__init__(file, channel_title, channel_link, channel_description,
                              generator=generator, *args, **kwargs)

        crawler_settings['FEED_EXPORTER'] = NoGeneratorRssItemExporter
        with CrawlerContext(crawler_settings=crawler_settings, **self.feed_settings):
            pass
        with open(self.feed_settings['feed_file']) as data, \
             open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'empty_feed_without_generator.rss')) as expected:
            self.assertUnorderedXmlEquivalentOutputs(data.read(), expected.read(), excepted_elements='lastBuildDate')

        class InvalidExporter(object):
            pass

        crawler_settings['FEED_EXPORTER'] = InvalidExporter
        with self.assertRaisesRegexp(TypeError, 'FEED_EXPORTER'):
            with CrawlerContext(crawler_settings=crawler_settings, **self.feed_settings):
                pass

    def test_item_validation(self):
        invalid_item = RssItem()
        invalid_item.enclosure.url = 'http://example.com/content'

        with self.assertRaisesRegexp(InvalidRssItemAttributesError, 'required attributes .*? not set'):
            with CrawlerContext(**self.feed_settings) as context:
                context.ipm.process_item(invalid_item, context.spider)

        class NonStandardElement(ItemElement):
            first_attribute = ItemElementAttribute(required=True, is_content=True)
            second_attribute = ItemElementAttribute(required=True)

        class NonStandardItem(RssItem):
            element = NonStandardElement()

        invalid_item = NonStandardItem()
        with self.assertRaisesRegexp(InvalidElementValueError, 'Could not assign'):
            invalid_item.element = 'valid value'
        invalid_item.element.first_attribute = 'valid value'

        with self.assertRaisesRegexp(InvalidRssItemAttributesError, 'required attributes .*? not set'):
            with CrawlerContext(**self.feed_settings) as context:
                context.ipm.process_item(invalid_item, context.spider)

        class InvalidSuperItem1(ExtendableItem):
            pass

        class InvalidSuperItem2(ExtendableItem):
            field = scrapy.Field()

        class InvalidSuperItem3(ExtendableItem):
            rss = scrapy.Field()

        for invalid_item_cls in (InvalidSuperItem1, InvalidSuperItem2, InvalidSuperItem3):
            with self.assertRaisesRegexp(InvalidRssItemError, "Item must have 'rss'"):
                with CrawlerContext(**self.feed_settings) as context:
                    context.ipm.process_item(invalid_item_cls(), context.spider)

    def test_single_item_in_the_feed(self):
        class SuperItem(ExtendableItem):
            some_field = scrapy.Field()

            def __init__(self):
                super(SuperItem, self).__init__()
                self.rss = RssItem()

        for item_name, item in self.items.items():
            with CrawlerContext(**self.feed_settings) as context:
                context.ipm.process_item(item, context.spider)
            with open(self.feed_settings['feed_file']) as data, \
                 open(os.path.join(os.path.dirname(__file__),
                                   'expected_rss', '{}.rss'.format(item_name))) as expected:
                self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

            super_item = SuperItem()
            super_item.rss = item
            with CrawlerContext(**self.feed_settings) as context:
                context.ipm.process_item(super_item, context.spider)
            with open(self.feed_settings['feed_file']) as data, \
                 open(os.path.join(os.path.dirname(__file__),
                                   'expected_rss', '{}.rss'.format(item_name))) as expected:
                self.assertUnorderedXmlEquivalentOutputs(data=data.read(), expected=expected.read())

    def test_all_items_in_the_single_feed(self):
        with open(os.path.join(os.path.dirname(__file__), 'expected_rss', 'empty_feed.rss'), 'rb') as feed_f:
            feed_tree = etree.fromstring(feed_f.read())
            feed_channel = feed_tree.xpath('//channel')[0]
            with CrawlerContext(**self.feed_settings) as context:
                for item_name, item in self.items.items():
                    context.ipm.process_item(item, context.spider)
                    with open(os.path.join(os.path.dirname(__file__),
                                           'expected_rss', '{}.rss'.format(item_name)), 'rb') as item_f:
                        item_tree = etree.fromstring(item_f.read())
                        feed_channel.extend(item_tree.xpath('//item'))
            with open(self.feed_settings['feed_file']) as data:
                self.assertUnorderedXmlEquivalentOutputs(data.read(), feed_tree)


class TestScraper:
    class MySpider(scrapy.Spider):
        name = 'spider'

    def test_spider_output_handling(self):
        spider = self.MySpider()
        scraper = Scraper(Crawler(self.MySpider))
        scraper.open_spider(spider)
        scraper._process_spidermw_output(RssItem(), None, None, None)
        scraper._process_spidermw_output(ExtendableItem(), None, None, None)
        scraper._process_spidermw_output(RssedItem(), None, None, None)
        scraper.close_spider(spider)


if __name__ == '__main__':
    unittest.main()

