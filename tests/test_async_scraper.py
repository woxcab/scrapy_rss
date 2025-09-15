# -*- coding: utf-8 -*-
import sys
from packaging.version import Version
import pytest
import scrapy
from scrapy.crawler import Crawler
from scrapy.core.scraper import Scraper

from scrapy_rss.items import RssItem, FeedItem, RssedItem
from tests import predefined_items

if Version(scrapy.__version__) >= Version('2.13'):
    import asyncio
    from twisted.internet import reactor # not used but it's required

    class TestAsyncScraper:
        class MySpider(scrapy.Spider):
            name = 'spider'
            custom_settings = {}

        @pytest.mark.parametrize("twisted_reactor,init_reactor", [
            (None, False),
            ('twisted.internet.epollreactor.EPollReactor', False),
            ('twisted.internet.asyncioreactor.AsyncioSelectorReactor', True),
        ])
        async def test_spider_output_handling(self, twisted_reactor, init_reactor):
            spider = self.MySpider()
            spider.custom_settings['TWISTED_REACTOR'] = twisted_reactor
            if init_reactor and "twisted.internet.reactor" in sys.modules:
                del sys.modules["twisted.internet.reactor"]
            crawler = Crawler(self.MySpider, init_reactor=init_reactor)
            try:
                crawler._apply_settings()
            except AttributeError:
                pass
            scraper = Scraper(crawler)
            scraper.open_spider(spider)
            scraper.crawler.spider = spider

            NSItem0 = predefined_items.NSItem0
            NSItem1 = predefined_items.NSItem1
            NSItem2 = predefined_items.NSItem2

            dummy_params = (None,)
            await scraper._process_spidermw_output(RssItem(), *dummy_params).asFuture(
                asyncio.get_running_loop())
            await scraper._process_spidermw_output(NSItem0(), *dummy_params).asFuture(
                asyncio.get_running_loop())
            await scraper._process_spidermw_output(NSItem1(), *dummy_params).asFuture(
                asyncio.get_running_loop())
            await scraper._process_spidermw_output(NSItem2(), *dummy_params).asFuture(
                asyncio.get_running_loop())
            await scraper._process_spidermw_output(FeedItem(), *dummy_params).asFuture(
                asyncio.get_running_loop())
            await scraper._process_spidermw_output(RssedItem(), *dummy_params).asFuture(
                asyncio.get_running_loop())
            scraper.close_spider()