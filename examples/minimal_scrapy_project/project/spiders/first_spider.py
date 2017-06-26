# -*- coding: utf-8 -*-
import scrapy

from scrapy_rss import RssItem


class SomeSpider(scrapy.Spider):
    name = 'first_spider'
    start_urls = ['https://woxcab.github.io/scrapy_rss/']

    def parse(self, response):
        for category_name in response.css('.list-group-item ::text'):
            item = RssItem()
            item.title = category_name.extract()
            yield item
