# -*- coding: utf-8 -*-

import scrapy_rss
import dateparser


class FillPipeline:
    def process_item(self, item, spider):
        if isinstance(item, scrapy_rss.RssedItem):
            item.rss.title = '{} [{}] [{}] [{}]'.format(item['name'], item['rating'],
                                                        item['reviews'], item['price'])
            if item['review_dates']:
                item.rss.pubDate = dateparser.parse(item['review_dates'][0],
                                                    settings={'RETURN_AS_TIMEZONE_AWARE': True})
        return item