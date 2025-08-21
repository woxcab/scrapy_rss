# -*- coding: utf-8 -*-

class InvalidAttributeValueError(ValueError):
    def __init__(self, attr_name, value):
        self.attr_name = attr_name
        self.value = value

    def __str__(self):
        return ("Could not assign value <{value}> to attribute '{attr_name}': "
                "attribute value cannot be instance of ElementAttribute class"
                .format(value=self.value, attr_name=self.attr_name))


class InvalidElementValueError(ValueError):
    def __init__(self, elem_name, elem_cls, value):
        self.elem_name = elem_name
        self.elem_cls = elem_cls
        self.value = value

    def __str__(self):
        return ("Could not assign value <{value}> to element <{elem_name}> of class <{elem_cls}>. "
                "For attributes modification use properties: element.attribute_name = attribute_value. "
                "For multiple allowed elements use list: category_element = ['cat1', 'cat2', 'cat3']"
                .format(value=self.value, elem_name=self.elem_name, elem_cls=self.elem_cls))


class InvalidRssItemError(ValueError):
    pass


class InvalidRssItemAttributesError(ValueError):
    def __init__(self, rss_element, required_attrs, content_arg):
        self.rss_element = rss_element
        self.required_attrs = required_attrs
        self.content_arg = content_arg

    def __str__(self):
        if self.content_arg:
            return "The next required attributes of RSS element '{}' ({}) "\
                   "or required content ('{}' argument) are not set" \
                   .format(self.rss_element, ", ".join(str(a) for a in self.required_attrs), self.content_arg)
        return "The next required attributes of RSS element '{}' are not set: {}" \
            .format(self.rss_element, ", ".join(str(a) for a in self.required_attrs))


class NoNamespaceURIError(ValueError):
    pass
