
from scrapy_rss.exporters import FeedItemExporter


class CustomRssItemExporter(FeedItemExporter):
    def __init__(self, *args, **kwargs):
        super(CustomRssItemExporter, self).__init__(*args, **kwargs)
        self.channel.generator = 'Special generator'
        self.channel.language = 'en-us'
        self.channel.managingEditor = 'editor@example.com'
        self.channel.category = ['category 1', 'category 2']
        self.channel.image.url = 'https://example.com/img.jpg'


