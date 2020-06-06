# -*- coding: utf-8 -*-

import unittest


class TestImport(unittest.TestCase):
    def test_module_level(self):
        from scrapy_rss import RssItem
        from scrapy_rss import ExtendableItem
        from scrapy_rss import RssedItem
        import scrapy_rss

    def test_elements(self):
        from scrapy_rss.elements import TitleElement
        from scrapy_rss.elements import LinkElement
        from scrapy_rss.elements import DescriptionElement
        from scrapy_rss.elements import AuthorElement
        from scrapy_rss.elements import CategoryElement
        from scrapy_rss.elements import CommentsElement
        from scrapy_rss.elements import EnclosureElement
        from scrapy_rss.elements import GuidElement
        from scrapy_rss.elements import PubDateElement
        from scrapy_rss.elements import SourceElement

    def test_exporters(self):
        from scrapy_rss.exporters import RssItemExporter

    def test_items(self):
        from scrapy_rss.items import RssItem
        from scrapy_rss.items import ExtendableItem
        from scrapy_rss.items import RssedItem

    def test_meta(self):
        from scrapy_rss.meta import BaseNSComponent
        from scrapy_rss.meta import NSComponentName
        from scrapy_rss.meta import ItemElementAttribute
        from scrapy_rss.meta import ItemElementMeta
        from scrapy_rss.meta import ItemElement
        from scrapy_rss.meta import MultipleElements
        from scrapy_rss.meta import ItemMeta
        from scrapy_rss.meta import BaseFeedItem

    def test_pipelines(self):
        from scrapy_rss.pipelines import RssExportPipeline

    def test_utils(self):
        from scrapy_rss.utils import format_rfc822


if __name__ == '__main__':
    unittest.main()
