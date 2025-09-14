# -*- coding: utf-8 -*-

from datetime import datetime
from scrapy_rss.rss import channel_elements
from scrapy_rss.exporters import FeedItemExporter


class CustomRssItemExporter(FeedItemExporter):
    def __init__(self, *args, **kwargs):
        super(CustomRssItemExporter, self).__init__(*args, **kwargs)
        self.channel.generator = 'Special generator'
        self.channel.language = 'en-us'
        self.channel.managingEditor = 'editor@example.com'
        self.channel.webMaster = 'webmaster@example.com'
        self.channel.copyright = 'Copyright 2025'
        self.channel.pubDate = datetime(2025, 9, 10, 13, 0, 0)

        self.channel.category = ['category 1', 'category 2']
        self.channel.category.append('category 3')
        self.channel.category.extend(['category 4', 'category 5'])

        # initialize image from dict
        self.channel.image = {
            'url': 'https://example.com/img.jpg',
            'description': 'Image link hover text',
        }
        # or initialize image from ImageElement
        self.channel.image = channel_elements.ImageElement(url='https://example.com/img.jpg')
        # or initialize image by each attribute
        self.channel.image.url = 'https://example.com/img.jpg' # required attribute of image
        self.channel.image.title = 'Image title' # optional
        self.channel.image.link = 'https://example.com/page' # optional
        self.channel.image.description = 'Image link hover text' # optional
        self.channel.image.width = 140 # optional
        self.channel.image.height = 350 # optional

        self.channel.docs = 'https://example.com/rss_docs'
        self.channel.cloud = {
            'domain': 'rpc.sys.com',
            'port': '80',
            'path': '/RPC2',
            'registerProcedure': 'myCloud.rssPleaseNotify',
            'protocol': 'xml-rpc'
        }
        self.channel.ttl = 60
        self.channel.rating = 4.0
        self.channel.textInput = channel_elements.TextInputElement(
            title='Input title',
            description='Description of input',
            name='Input name',
            link='http://example.com/cgi.py'
        )

        self.channel.skipHours = (0, 1, 3, 7, 23) # initialize list from iterable
        self.channel.skipHours = 12 # or initialize list with single value

        self.channel.skipDays = 14 # initialize list with single value
        self.channel.skipDays = [1, 14] # or initialize list from list
