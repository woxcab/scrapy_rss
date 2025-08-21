# -*- coding: utf-8 -*-

from .nscomponent import NSComponentName
from .attribute import ElementAttribute
from ..exceptions import InvalidElementValueError, InvalidAttributeValueError


def _build_component_setter(name):
    """
    Build attribute or element setter

    Parameters
    ----------
    name : NSComponentName
        name of an attribute or child element
    """

    def setter(self, value):
        component = getattr(self, name.priv_name)
        if isinstance(component, ElementAttribute):
            if isinstance(value, ElementAttribute):
                raise InvalidAttributeValueError(name, value)
            component.value = value
        elif any('{}.{}'.format(cls.__module__,
                                cls.__name__) == 'scrapy_rss.meta.element.MultipleElements'
                 for cls in component.__class__.mro()): # isinstance(value, MultipleElements)
            component.clear()
            component.add(value)
        elif isinstance(value, component.__class__):
            setattr(self, name.priv_name, value)
        elif any('{}.{}'.format(cls.__module__,
                                cls.__name__) == 'scrapy_rss.meta.element.Element'
                 for cls in value.__class__.mro()): # isinstance(value, Element)
            raise InvalidElementValueError(name, component.__class__, value)
        elif isinstance(value, dict):
            setattr(self, name.priv_name, component.__class__(**value))
        elif not component.required_attrs and component.content_arg:
            setattr(component, component.content_arg.pub_name, value)
        else:
            raise InvalidElementValueError(name, component.__class__, value)
        self._assigned = value is not None

    return setter
