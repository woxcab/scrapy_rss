# -*- coding: utf-8 -*-

import six
from scrapy import signals
from scrapy.exceptions import NotConfigured, CloseSpider
from scrapy.utils.misc import load_object

from .items import RssItem
from .exporters import RssItemExporter


class RssExportPipeline(object):
    def __init__(self):
        self.files = {}
        self.exporters = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        try:
            file = open(spider.settings.get('FEED_FILE'), 'wb')
        except TypeError:
            raise NotConfigured('FEED_FILE parameter does not string or does not exist')
        except (IOError, OSError) as e:
            raise CloseSpider('Cannot open file {}: {}'.format(spider.settings.get('FEED_FILE', None), e))
        self.files[spider] = file
        feed_title = spider.settings.get('FEED_TITLE')
        if not feed_title:
            raise NotConfigured('FEED_TITLE parameter does not exist')
        feed_link = spider.settings.get('FEED_LINK')
        if not feed_link:
            raise NotConfigured('FEED_LINK parameter does not exist')
        feed_description = spider.settings.get('FEED_DESCRIPTION')
        if feed_description is None:
            raise NotConfigured('FEED_DESCRIPTION parameter does not exist')

        item_cls = spider.settings.get('FEED_ITEM_CLASS', spider.settings.get('FEED_ITEM_CLS', RssItem))
        if isinstance(item_cls, six.string_types):
            item_cls = load_object(item_cls)

        namespaces = spider.settings.get('FEED_NAMESPACES', {})

        feed_exporter = spider.settings.get('FEED_EXPORTER', RssItemExporter)
        if isinstance(feed_exporter, six.string_types):
            feed_exporter = load_object(feed_exporter)
        if not issubclass(feed_exporter, RssItemExporter):
            raise TypeError("FEED_EXPORTER must be RssItemExporter or its subclass, not '{}'".format(feed_exporter))
        self.exporters[spider] = feed_exporter(file, feed_title, feed_link, feed_description,
                                               namespaces=namespaces, item_cls=item_cls)
        self.exporters[spider].start_exporting()

    def spider_closed(self, spider):
        self.exporters[spider].finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporters[spider].export_item(item)
        return item
