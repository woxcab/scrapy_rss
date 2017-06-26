
from scrapy_rss.exporters import RssItemExporter


class CustomRssItemExporter(RssItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs['generator'] = kwargs.get('generator', 'Special generator')
        kwargs['language'] = kwargs.get('language', 'en-us')
        super(CustomRssItemExporter, self).__init__(*args, **kwargs)


