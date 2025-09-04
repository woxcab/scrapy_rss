# -*- coding: utf-8 -*-

class InvalidComponentNameError(ValueError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return ("Cannot use special property <{0}> as a component name. "
                "Use arbitrary number of trailing underscores sush as <{0}_> "
                "that're ignored on XML exporting"
                .format(self.name))


class InvalidAttributeValueError(ValueError):
    def __init__(self, attr_name, value):
        self.attr_name = attr_name
        self.value = value

    def __str__(self):
        return ("Could not assign value <{value}> to attribute '{attr_name}': "
                "attribute value cannot be instance of ElementAttribute class"
                .format(value=self.value, attr_name=self.attr_name))


class InvalidElementValueError(ValueError):
    def __init__(self, elem_name, elem_cls, value, msg=None):
        self.elem_name = elem_name
        self.elem_cls = elem_cls
        self.value = value
        self.msg = msg

    def __str__(self):
        msg = ": {}.".format(self.msg) if self.msg else "."
        return ("Could not assign value {value!r} to element <{elem_name}> of class {elem_cls}{msg} "
                "For attributes modification use properties: element.attribute_name = attribute_value. "
                "For multiple allowed elements use list: category_element = ['cat1', 'cat2', 'cat3']"
                .format(value=self.value, msg=msg, elem_name=self.elem_name, elem_cls=self.elem_cls))


class InvalidFeedItemError(ValueError):
    pass


class InvalidFeedItemComponentsError(ValueError):
    def __init__(self, element):
        """

        Parameters
        ----------
        element : Element
        """
        self.element = element

    def __str__(self):
        req_attrs = ''
        req_elems = ''
        if self.element.required_attrs:
            req_attrs = 'required attributes: ' + ", ".join(map(str, self.element.required_attrs))
        if self.element.required_children:
            req_elems = 'required children: ' + ", ".join(map(str, self.element.required_children))

        return ("Missing one or more required components of feed element '{}': {}"
                .format(self.element, "; ".join(filter(bool, [req_attrs, req_elems])))
        )


class NoNamespaceURIError(ValueError):
    pass
