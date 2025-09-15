# -*- coding: utf-8 -*-

BOT_NAME = 'project'

SPIDER_MODULES = ['project.spiders']

ITEM_PIPELINES = {
    'project.pipelines.FillPipeline': 500,
    'scrapy_rss.pipelines.FeedExportPipeline': 950,
}

FEED_FILE = 'feed.rss'
FEED_TITLE = 'Shop items'
FEED_LINK = 'http://example.com/rss'
FEED_DESCRIPTION = 'List of shop items'

FEED_EXPORTER = 'project.exporters.CustomRssItemExporter'
