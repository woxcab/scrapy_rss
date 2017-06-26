# -*- coding: utf-8 -*-

import scrapy
from scrapy_rss import RssedItem


class ShopItem(RssedItem):
    name = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    reviews = scrapy.Field()
    review_dates = scrapy.Field()

