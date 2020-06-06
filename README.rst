==========
scrapy_rss
==========

.. image:: https://img.shields.io/pypi/v/scrapy_rss.svg
   :target: https://pypi.python.org/pypi/scrapy_rss
   :alt: PyPI Version

.. image:: https://img.shields.io/travis/woxcab/scrapy_rss/master.svg
   :target: http://travis-ci.org/woxcab/scrapy_rss
   :alt: Build Status

.. image:: https://img.shields.io/badge/wheel-yes-brightgreen.svg
   :target: https://pypi.python.org/pypi/scrapy_rss
   :alt: Wheel Status

.. image:: https://img.shields.io/codecov/c/github/woxcab/scrapy_rss/master.svg
   :target: http://codecov.io/github/woxcab/scrapy_rss?branch=master
   :alt: Coverage report

Tools to easy generate `RSS feed <http://www.rssboard.org/rss-specification>`_ that contains each scraped item using `Scrapy framework <https://github.com/scrapy/scrapy>`_.

Package works with Python 2.7, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8 and 3.9.

If you use Python 3.3 then you have to use Scrapy<1.5.0.

If you use Python 2.7 then you have to use Scrapy<2.0.



Table of Contents
=================
* `Installation <#installation>`__
* `How To Use <#how-to-use>`__

  * `Configuration <#configuration>`__
  * `Optional Additional Customization <#feed-channel-elements-customization-optionally>`__
  * `Usage <#usage>`__
  
    * `Basic usage <#basic-usage>`__
    * `RssItem derivation and namespaces <#rssitem-derivation-and-namespaces>`__

* `Scrapy Project Examples <#scrapy-project-examples>`__


`Installation <https://packaging.python.org/installing/>`_
==========================================================
* Install :code:`scrapy_rss` using pip

  .. code:: bash

       pip install scrapy_rss

  or using pip for the specific interpreter, e.g.:

  .. code:: bash

      pip3 install scrapy_rss

* or using setuptools directly:

  .. code:: bash

      cd path/to/root/of/scrapy_rss
      python setup.py install

  or using setuptools for specific interpreter, e.g.:

  .. code:: bash

      cd path/to/root/of/scrapy_rss
      python3 setup.py install


How To Use
==========

Configuration
-------------

Add parameters to the Scrapy project settings (`settings.py` file)
or to the :code:`custom_settings` attribute of the spider:

1. Add item pipeline that export items to rss feed:

   .. code:: python

     ITEM_PIPELINES = {
         # ...
         'scrapy_rss.pipelines.RssExportPipeline': 900,  # or another priority
         # ...
     }


2. Add required feed parameters:

   FEED_FILE
       the absolute or relative file path where the result RSS feed will be saved.
       For example, :code:`feed.rss` or :code:`output/feed.rss`.
   FEED_TITLE
       the name of the channel (feed),
   FEED_DESCRIPTION
       the phrase or sentence that describes the channel (feed),
   FEED_LINK
       the URL to the HTML website corresponding to the channel (feed)

   .. code:: python

     FEED_FILE = 'path/to/feed.rss'
     FEED_TITLE = 'Some title of the channel'
     FEED_LINK = 'http://example.com/rss'
     FEED_DESCRIPTION = 'About channel'


Feed (Channel) Elements Customization [optionally]
--------------------------------------------------

If you want to change other channel parameters (such as language, copyright, managing_editor,
webmaster, pubdate, last_build_date, category, generator, docs, ttl)
then define your own exporter that's inherited from :code:`RssItemExporter` class, for example:

.. code:: python

   from scrapy_rss.exporters import RssItemExporter

   class MyRssItemExporter(RssItemExporter):
      def __init__(self, *args, **kwargs):
         kwargs['generator'] = kwargs.get('generator', 'Special generator')
         kwargs['language'] = kwargs.get('language', 'en-us')
         super(CustomRssItemExporter, self).__init__(*args, **kwargs)

And add :code:`FEED_EXPORTER` parameter to the Scrapy project settings
or to the :code:`custom_settings` attribute of the spider:

.. code:: python

   FEED_EXPORTER = 'myproject.exporters.MyRssItemExporter'


Usage
-----
Basic usage
^^^^^^^^^^^

Declare your item directly as RssItem():

.. code:: python

  import scrapy_rss

  item1 = scrapy_rss.RssItem()

Or use predefined item class :code:`RssedItem` with RSS field named as :code:`rss`
that's instance of :code:`RssItem`:

.. code:: python

  import scrapy
  import scrapy_rss

  class MyItem(scrapy_rss.RssedItem):
      field1 = scrapy.Field()
      field2 = scrapy.Field()
      # ...

  item2 = MyItem()


Set/get item fields. Case sensitive attributes of :code:`RssItem()` are appropriate to RSS elements.
Attributes of RSS elements are case sensitive too.
If the editor allows autocompletion then it suggests attributes for instances of :code:`RssedItem` and :code:`RssItem`.
It's allowed to set **any** subset of RSS elements (e.g. title only). For example:

.. code:: python

  from datetime import datetime

  item1.title = 'RSS item title'  # set value of <title> element
  title = item1.title.title  # get value of <title> element
  item1.description = 'description'

  item1.guid = 'item identifier'
  item1.guid.isPermaLink = True  # set value of attribute isPermalink of <guid> element,
                                 # isPermaLink is False by default
  is_permalink = item1.guid.isPermaLink  # get value of attribute isPermalink of <guid> element
  guid = item1.guid.guid  # get value of element <guid>

  item1.category = 'single category'
  category = item1.category
  item1.category = ['first category', 'second category']
  first_category = item1.category[0].category # get value of the element <category> with multiple values
  all_categories = [cat.category for cat in item1.category]

  # direct attributes setting
  item1.enclosure.url = 'http://example.com/file'
  item1.enclosure.length = 0
  item1.enclosure.type = 'text/plain'

  # or dict based attributes setting
  item1.enclosure = {'url': 'http://example.com/file', 'length': 0, 'type': 'text/plain'}
  item1.guid = {'guid': 'item identifier', 'isPermaLink': True}

  item1.pubDate = datetime.now()  # correctly works with Python' datetimes


  item2.rss.title = 'Item title'
  item2.rss.guid = 'identifier'
  item2.rss.enclosure = {'url': 'http://example.com/file', 'length': 0, 'type': 'text/plain'}


All allowed elements are listed in the `scrapy_rss/items.py <https://github.com/woxcab/scrapy_rss/blob/master/scrapy_rss/items.py>`_.
All allowed attributes of each element with constraints and default values
are listed in the `scrapy_rss/elements.py <https://github.com/woxcab/scrapy_rss/blob/master/scrapy_rss/elements.py>`_.
Also you can read `RSS specification <http://www.rssboard.org/rss-specification>`_ for more details.

:code:`RssItem` derivation and namespaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can extend RssItem to add new XML fields that can be namespaced or not.
You can specify namespaces in an attribute and/or an element constructors.
Namespace prefix can be specified in the attribute/element name
using double underscores as delimiter (:code:`prefix__name`)
or in the attribute/element constructor using :code:`ns_prefix` argument. 
Namespace URI can be specified using :code:`ns_uri` argument of the constructor.

.. code:: python

    from scrapy_rss.meta import ItemElementAttribute, ItemElement
    from scrapy_rss.items import RssItem

    class Element0(ItemElement):
        # attributes without special namespace
        attr0 = ItemElementAttribute(is_content=True, required=True)
        attr1 = ItemElementAttribute()

    class Element1(ItemElement):
        # attribute "prefix2:attr2" with namespace xmlns:prefix2="id2"
        attr2 = ItemElementAttribute(ns_prefix="prefix2", ns_uri="id2")

        # attribute "prefix3:attr3" with namespace xmlns:prefix3="id3"
        prefix3__attr3 = ItemElementAttribute(ns_uri="id3")

        # attribute "prefix4:attr4" with namespace xmlns:prefix4="id4"
        fake_prefix__attr4 = ItemElementAttribute(ns_prefix="prefix4", ns_uri="id4")

        # attribute "attr5" with default namespace xmlns="id5"
        attr5 = ItemElementAttribute(ns_uri="id5")

    class MyXMLItem(RssItem):
        # element <elem1> without namespace
        elem1 = Element0()

        # element <elem_prefix2:elem2> with namespace xmlns:elem_prefix2="id2e"
        elem2 = Element0(ns_prefix="elem_prefix2", ns_uri="id2e")

        # element <elem_prefix3:elem3> with namespace xmlns:elem_prefix3="id3e"
        elem_prefix3__elem3 = Element1(ns_uri="id3e")

        # yet another element <elem_prefix4:elem3> with namespace xmlns:elem_prefix4="id4e"
        # (does not conflict with previous one)
        fake_prefix__elem3 = Element0(ns_prefix="elem_prefix4", ns_uri="id4e")

        # element <elem5> with default namespace xmlns="id5e"
        elem5 = Element0(ns_uri="id5e")

Access to elements and its attributes is the same as with simple items:

.. code:: python

    item = MyXMLItem()
    item.title = 'Some title'
    item.elem1.attr0 = 'Required content value'
    item.elem1 = 'Another way to set content value'
    item.elem1.attr1 = 'Some attribute value'
    item.elem_prefix3__elem3.prefix3__attr3 = 'Yet another attribute value'
    item.elem_prefix3__elem3.fake_prefix__attr4 = '' # non-None value is interpreted as assigned
    item.fake_prefix__elem3.attr1 = 42


Several optional settings are allowed for namespaced items:

FEED_NAMESPACES
  list of tuples :code:`[(prefix, URI), ...]` or dictionary :code:`{prefix: URI, ...}` of namespaces
  that must be defined in the root XML element

FEED_ITEM_CLASS or FEED_ITEM_CLS
  main class of feed items (class object :code:`MyXMLItem` or path to class :code:`"path.to.MyXMLItem"`).
  **Default value**: :code:`RssItem`.
  It's used in order to extract all possible namespaces
  that will be declared in the root XML element.

  Feed items do **NOT** have to be instances of this class or its subclass.

If these settings are not defined or only part of namespaces are defined
then other used namespaces will be declared either in the :code:`<item>` element
or in its subelements when these namespaces are not unique.
Each :code:`<item>` element and its sublements always contains
only namespace declarations of non-:code:`None` attributes (including ones that are interpreted as element content).


Scrapy Project Examples
=======================

`Examples directory <https://github.com/woxcab/scrapy_rss/blob/master/examples>`_ contains
several Scrapy projects with the scrapy_rss usage demonstration. It crawls
`this website <https://woxcab.github.io/scrapy_rss/>`_ whose source code is
`here <https://github.com/woxcab/scrapy_rss/blob/master/examples/website>`_.

Just go to the Scrapy project directory and run commands

.. code:: bash

   scrapy crawl first_spider
   scrapy crawl second_spider

Thereafter `feed.rss` and `feed2.rss` files will be created in the same directory.
