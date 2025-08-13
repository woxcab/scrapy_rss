# -*- coding: utf-8 -*-

from .nscomponent import BaseNSComponent, NSComponentName
from .attribute import ElementAttribute
from .element import ElementMeta, Element, MultipleElements
from .item import ItemMeta, FeedItem

# backward compatibility
from .attribute import ItemElementAttribute
from .element import ItemElementMeta, ItemElement
from .item import ExtendableItem
