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

Tools for easy generating of RSS feed with each scraped item using `Scrapy framework <https://github.com/scrapy/scrapy>`_.

Package works with Python 2.7, 3.3, 3.4 and 3.5.


`Installation <https://packaging.python.org/installing/>`_
==========================================================
* Install :code:`scrapy_rss` using pip

  .. code:: bash

       pip install scrapy_rss

  or using pip for specific interpreter, e.g.:

  .. code:: bash

      pip3 install scrapy_rss

* or using directly setuptools:

  .. code:: bash

      cd path/to/root/of/scrapy_rss
      python setup.py install

  or using setuptools for specific interpreter, e.g.:

  .. code:: bash

      cd path/to/root/of/scrapy_rss
      python3 setup.py install


How To Use
==========

Add parameters to the Scrapy project settings (settings.py file)
or to the :code:`custom_settings` attribute of the spider:

1. Add item pipeline that export items to rss feed:
   ::

     ITEM_PIPELINES = {
         # ...
         'scrapy_rss.pipelines.RssExportPipeline': 900,  # or another priority
         # ...
     }


2. Add required feed parameters:

   FEED_FILE
       absolute or relative file path where the result RSS feed will be saved.
       For example, :code:`feed.rss` or :code:`output/feed.rss`.
   FEED_TITLE
       the name of the channel (feed),
   FEED_DESCRIPTION
       phrase or sentence describing the channel (feed),
   FEED_LINK
       the URL to the HTML website corresponding to the channel (feed)
   ::

     FEED_FILE = 'path/to/feed.rss'
     FEED_TITLE = 'Some title of the channel'
     FEED_LINK = 'http://example.com/rss'
     FEED_DESCRIPTION = 'About channel'


Declare your item directly as RssItem():

.. code:: python

  import scrapy_rss

  item1 = scrapy_rss.RssItem()

Or define new item class with RSS field named as :code:`rss`:

.. code:: python

  import scrapy_rss

  class MyItem(scrapy_rss.ExtendableItem):
      # scrapy.Field() and/or another fields definitions
      # ...

      def __init__(self):
          super(MyItem, self).__init__()
          self.rss = scrapy_rss.RssItem()

  item2 = MyItem()


Set/get item fields. Case sensitive attributes of :code:`RssItem()` are appropriate to RSS elements,
Attributes of RSS elements are case sensitive too.
If editor is allowed autocompletion then it suggests attributes for instances of :code:`RssItem`.
It's allowed to set **any** subset of RSS elements (e.g. only title). For example:

.. code:: python

  item1.title = 'RSS item title'  # set value of <title> element
  title = item1.title.title  # get value of <title> element
  item1.description = 'description'

  item1.guid = 'item identifier'
  item1.guid.isPermaLink = True  # set value of attribute isPermalink of <guid> element,
                                 # isPermaLink is False by default
  is_permalink = item1.guid.isPermaLink  # get value of attribute isPermalink of <guid> element
  guid = item1.guid.guid  # set guid to 'item identifier'

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


  item2.rss.title = 'Item title'
  item2.rss.guid = 'identifier'
  item2.rss.enclosure = {'url': 'http://example.com/file', 'length': 0, 'type': 'text/plain'}


All allowed elements are listed in the `scrapy_rss/items.py <scrapy_rss/items.py>`_.
All allowed attributes of each element with constraints and default values
are listed in the `scrapy_rss/elements.py <scrapy_rss/elements.py>`_.
