# -*- coding: utf-8 -*-


class ItemElementAttribute:
    def __init__(self, value=None, serializer=lambda x: str(x), required=False, is_content=False):
        self.__required = required
        self.__is_content = is_content
        self.serializer = serializer
        self.value = value

    @property
    def required(self):
        return self.__required

    @property
    def is_content(self):
        return self.__is_content
