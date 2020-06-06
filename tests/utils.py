# -*- coding: utf-8 -*-

from collections import Counter
import itertools

from unittest.util import safe_repr
import difflib
import re
from os.path import commonprefix
import sys
import pprint
import six

from twisted.python.failure import Failure
from scrapy.pipelines import ItemPipelineManager
from frozendict import frozendict
from lxml import etree
from xmlunittest import XmlTestCase

from scrapy_rss.meta import ItemElement, MultipleElements
from scrapy_rss.items import RssItem

try:
    from unittest.util import _common_shorten_repr, _shorten
except ImportError:
    _MAX_LENGTH = 80
    _PLACEHOLDER_LEN = 12
    _MIN_BEGIN_LEN = 5
    _MIN_END_LEN = 5
    _MIN_COMMON_LEN = 5
    _MIN_DIFF_LEN = _MAX_LENGTH - \
                    (_MIN_BEGIN_LEN + _PLACEHOLDER_LEN + _MIN_COMMON_LEN +
                     _PLACEHOLDER_LEN + _MIN_END_LEN)
    assert _MIN_DIFF_LEN >= 0


    def _shorten(s, prefixlen, suffixlen):
        skip = len(s) - prefixlen - suffixlen
        if skip > _PLACEHOLDER_LEN:
            s = '%s[%d chars]%s' % (s[:prefixlen], skip, s[len(s) - suffixlen:])
        return s


    def _common_shorten_repr(*args):
        args = tuple(map(safe_repr, args))
        maxlen = max(map(len, args))
        if maxlen <= _MAX_LENGTH:
            return args

        prefix = commonprefix(args)
        prefixlen = len(prefix)

        common_len = _MAX_LENGTH - \
                     (maxlen - prefixlen + _MIN_BEGIN_LEN + _PLACEHOLDER_LEN)
        if common_len > _MIN_COMMON_LEN:
            assert _MIN_BEGIN_LEN + _PLACEHOLDER_LEN + _MIN_COMMON_LEN + \
                   (maxlen - prefixlen) < _MAX_LENGTH
            prefix = _shorten(prefix, _MIN_BEGIN_LEN, common_len)
            return tuple(prefix + s[prefixlen:] for s in args)

        prefix = _shorten(prefix, _MIN_BEGIN_LEN, _MIN_COMMON_LEN)
        return tuple(prefix + _shorten(s[prefixlen:], _MIN_DIFF_LEN, _MIN_END_LEN)
                     for s in args)


def get_dict_attr(obj,attr):
    for obj in [obj]+obj.__class__.mro():
        if attr in obj.__dict__:
            return obj.__dict__[attr]
    raise AttributeError


class RaisedItemPipelineManager(ItemPipelineManager):
    def process_item(self, item, spider):
        d = super(RaisedItemPipelineManager, self).process_item(item, spider)
        if isinstance(d.result, Failure):
            failure = d.result
            d.addErrback(lambda failure: None)  # workaround for Python 2.*
            print(failure.getTraceback())
            failure.raiseException()
        return d


class UnorderedXmlTestCase(XmlTestCase):
    """
    Expand XmlTestCase functionality with unordered XML equivalence testing.
    """

    @classmethod
    def _xml_to_tuple(cls, element):
        return (element.tag,
                frozendict(element.nsmap),
                frozendict(element.attrib),
                frozendict(Counter(t for t in element.itertext() if t.strip())),
                frozenset(cls._xml_to_tuple(child) for child in element.getchildren()))

    @staticmethod
    def _str_to_bytes(data):
        if isinstance(data, str):
            return data.encode(encoding='utf-8')
        if not isinstance(data, bytes):
            raise ValueError("Passing data must be string or bytes array")
        return data

    def _getAssertEqualityFunc(self, first, second):
        for (first_cls, second_cls) in ((first.__class__, second.__class__),
                                        (first.__class__, None),
                                        (None, second.__class__)):
            if (first_cls, second_cls) in self._type_equality_funcs:
                asserter = self._type_equality_funcs[(first_cls, second_cls)]
                if asserter is not None:
                    if isinstance(asserter, str):
                        asserter = getattr(self, asserter)
                    return asserter
        return super(UnorderedXmlTestCase, self)._getAssertEqualityFunc(first, second)

    def assertUnorderedXmlEquivalentOutputs(self, data, expected, excepted_elements = ('lastBuildDate', 'generator')):
        """
        Children and text subnodes of each element in XML are considered as unordered set.
        Therefore if two XML files has different order of same elements then these XMLs are same.
        """
        if not excepted_elements:
            excepted_elements = ()
        if isinstance(excepted_elements, six.string_types):
            excepted_elements = (excepted_elements,)

        data = data if isinstance(data, etree._Element) \
            else etree.fromstring(self._str_to_bytes(data))
        for excepted_element in excepted_elements:
            for element in data.xpath('//{}'.format(excepted_element)):
                element.getparent().remove(element)
        data_tuple = self._xml_to_tuple(data)

        expected = expected if isinstance(expected, etree._Element) \
            else etree.fromstring(self._str_to_bytes(expected))
        for excepted_element in excepted_elements:
            for element in expected.xpath('//{}'.format(excepted_element)):
                element.getparent().remove(element)
        expected_tuple = self._xml_to_tuple(expected)

        if data_tuple != expected_tuple:
            self.fail(
                'Feeds are not equivalent accurate within ordering '
                '(taking into consideration excepted nodes {excepted_elements}):\n'
                'Given: {given}\n'
                'Expected: {expected}'
                .format(excepted_elements=excepted_elements,
                        given=etree.tostring(data), expected=etree.tostring(expected)))

    def assertXmlDocument(self, data):
        data = self._str_to_bytes(data)
        return super(UnorderedXmlTestCase, self).assertXmlDocument(data)

    def assertXmlEquivalentOutputs(self, data, expected):
        data = self._str_to_bytes(data)
        expected = self._str_to_bytes(expected)
        return super(UnorderedXmlTestCase, self).assertXmlEquivalentOutputs(data, expected)

    def assertSequenceEqual(self, seq1, seq2, msg=None, seq_type=None):
        """An equality assertion for ordered sequences (like lists and tuples).

        For the purposes of this function, a valid ordered sequence type is one
        which can be indexed, has a length, and has an equality operator.

        Args:
            seq1: The first sequence to compare.
            seq2: The second sequence to compare.
            seq_type: The expected datatype of the sequences, or None if no
                    datatype should be enforced.
            msg: Optional message to use on failure instead of a list of
                    differences.
        """
        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                raise self.failureException('First sequence is not a %s: %s'
                                        % (seq_type_name, safe_repr(seq1)))
            if not isinstance(seq2, seq_type):
                raise self.failureException('Second sequence is not a %s: %s'
                                        % (seq_type_name, safe_repr(seq2)))
        else:
            seq_type_name = "sequence"

        differing = None
        try:
            len1 = len(seq1)
        except (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % (
                    seq_type_name)

        if differing is None:
            try:
                len2 = len(seq2)
            except (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % (
                        seq_type_name)

        if differing is None:
            if len1 > len2:
                differing = ('\nFirst %s contains %d additional '
                              'elements.\n' % (seq_type_name, len1 - len2))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len2, seq1[len2]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of first %s\n' % (len2, seq_type_name))
            elif len1 < len2:
                differing = ('\nSecond %s contains %d additional '
                              'elements.\n' % (seq_type_name, len2 - len1))
                try:
                    differing += ('First extra element %d:\n%s\n' %
                                  (len1, seq2[len1]))
                except (TypeError, IndexError, NotImplementedError):
                    differing += ('Unable to index element %d '
                                  'of second %s\n' % (len1, seq_type_name))

            tmp_differing = ''
            for ind, (item1, item2) in enumerate(zip(seq1, seq2)):
                try:
                        self.assertEqual(item1, item2)
                except AssertionError as e:
                    tmp_differing += ('\nFirst differing element %d: %s\n' %
                                      (ind, e.args[0]))
                    break
            if tmp_differing:
                differing = '%ss differ: %s != %s\n%s' % (
                    (seq_type_name.capitalize(),) +
                    _common_shorten_repr(seq1, seq2) + (tmp_differing,))
            else:
                return

        standardMsg = differing
        diffMsg = '\n' + '\n'.join(
            difflib.ndiff(pprint.pformat(seq1).splitlines(),
                          pprint.pformat(seq2).splitlines()))

        standardMsg = self._truncateMessage(standardMsg, diffMsg)
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)


class RssTestCase(UnorderedXmlTestCase):
    def __init__(self, *args, **kwargs):
        super(RssTestCase, self).__init__(*args, **kwargs)
        for elem in RssItem().elements.values():
            if isinstance(elem, MultipleElements):
                self.addTypeEqualityFunc((elem.__class__, None), self.assertMultipleRssElementsEqualsToValues)
            else:
                self.addTypeEqualityFunc((elem.__class__, None), self.assertRssElementEqualsToValue)

    def assertRssElementEqualsToValue(self, element, value, msg=None):
        if isinstance(value, ItemElement):
            raise NotImplemented
        self.assertEqual(getattr(element, str(element.content_arg)), value, msg)

    def assertMultipleRssElementsEqualsToValues(self, multiple_element, values, msg=None):
        if isinstance(values, ItemElement):
            raise NotImplemented
        if len(multiple_element) == 1:
            self.assertRssElementEqualsToValue(multiple_element, values, msg)
        else:
            self.assertSequenceEqual([getattr(elem, str(elem.content_arg)) for elem in multiple_element], values, msg)


