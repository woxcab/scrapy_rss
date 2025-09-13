# -*- coding: utf-8 -*-

BOT_NAME = 'project'

SPIDER_MODULES = ['project.spiders']

ITEM_PIPELINES = {
    'scrapy_rss.pipelines.FeedExportPipeline': 950,
}

FEED_FILE = 'feed.rss'
FEED_TITLE = 'Shop categories'
FEED_LINK = 'http://example.com/rss'
FEED_DESCRIPTION = 'List of shop categories'
