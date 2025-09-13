# -*- coding: utf-8 -*-

from importlib import import_module
import sys
import pytest


class TestImport:
    ITEM_ELEMENTS_CLASSES = [
        'TitleElement',
        'LinkElement',
        'DescriptionElement',
        'AuthorElement',
        'CategoryElement',
        'CommentsElement',
        'EnclosureElement',
        'GuidElement',
        'PubDateElement',
        'SourceElement',
    ]

    def test_module_level(self):
        from scrapy_rss import RssItem
        from scrapy_rss import FeedItem
        from scrapy_rss import ExtendableItem
        from scrapy_rss import RssedItem
        import scrapy_rss

    @pytest.mark.parametrize('item_element_cls', ITEM_ELEMENTS_CLASSES)
    def test_item_elements(self, item_element_cls):
        item_elements_module = import_module('scrapy_rss.rss.item_elements')
        getattr(item_elements_module, item_element_cls)

    @pytest.mark.parametrize('item_element_cls', ITEM_ELEMENTS_CLASSES)
    def test_item_elements_from_old_path(self, item_element_cls):
        old_module_name = 'scrapy_rss.elements'
        if old_module_name in sys.modules:
            del sys.modules[old_module_name]
        with pytest.warns(DeprecationWarning, match='Use scrapy_rss.rss.item_elements'):
            old_module = import_module(old_module_name)
        old_element = getattr(old_module, item_element_cls)
        new_module = import_module('scrapy_rss.rss.item_elements')
        new_element = getattr(new_module, item_element_cls)
        assert old_element is new_element

    def test_exporters_module(self):
        from scrapy_rss.exporters import FeedItemExporter, RssItemExporter

    def test_items_module(self):
        from scrapy_rss.items import RssItem
        from scrapy_rss.items import FeedItem
        from scrapy_rss.items import RssedItem
        from scrapy_rss.rss.items import RssItem
        from scrapy_rss.rss.items import FeedItem
        from scrapy_rss.rss.items import RssedItem

    def test_meta_package(self):
        from scrapy_rss.meta import BaseNSComponent
        from scrapy_rss.meta import NSComponentName
        from scrapy_rss.meta import ElementAttribute
        from scrapy_rss.meta import ElementMeta
        from scrapy_rss.meta import Element
        from scrapy_rss.meta import MultipleElements
        from scrapy_rss.meta import ItemMeta
        from scrapy_rss.meta import FeedItem

    def test_rss_package(self):
        from scrapy_rss.rss import ChannelElement
        from scrapy_rss.rss import RssItem
        from scrapy_rss.rss import RssedItem

    @pytest.mark.parametrize('old_cls_name,new_cls_name,args',
                             [('ItemElementAttribute', 'ElementAttribute', []),
                              ('ItemElementMeta', 'ElementMeta', ['some_name', (), {}]),
                              ('ItemElement', 'Element', []),
                              ('ExtendableItem', 'FeedItem', [])])
    def test_old_meta_package(self, old_cls_name, new_cls_name, args):
        module = import_module('scrapy_rss.meta')
        old_cls = getattr(module, old_cls_name)
        new_cls = getattr(module, new_cls_name)
        assert issubclass(old_cls, new_cls)
        with pytest.warns(DeprecationWarning, match='Use {} class'.format(new_cls_name)):
            old_cls(*args)

    def test_pipelines_module(self):
        from scrapy_rss.pipelines import FeedExportPipeline
        from scrapy_rss.pipelines import RssExportPipeline

    def test_utils_module(self):
        from scrapy_rss.utils import get_tzlocal
        from scrapy_rss.utils import format_rfc822
        from scrapy_rss.utils import object_to_list
        from scrapy_rss.utils import is_strict_subclass
        from scrapy_rss.utils import get_full_class_name
        from scrapy_rss.utils import deprecated_module
        from scrapy_rss.utils import deprecated_class
        from scrapy_rss.utils import deprecated_func


if __name__ == '__main__':
    pytest.main()
