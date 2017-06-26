# -*- coding: utf-8 -*-
import scrapy

from scrapy_rss import RssItem


class SomeSpider(scrapy.Spider):
    name = 'second_spider'
    start_urls = ['https://woxcab.github.io/scrapy_rss/']
    custom_settings = {
        'FEED_TITLE': 'New shop categories',
        'FEED_FILE': 'feed2.rss'
    }

    def parse(self, response):
        for category_name in response.css('.list-group-item ::text'):
            item = RssItem()
            item.title = category_name.extract()
            yield item
