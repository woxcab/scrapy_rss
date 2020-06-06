# -*- coding: utf-8 -*-

import pytest
import re
from itertools import product, chain, combinations

from scrapy_rss.meta import BaseNSComponent, NSComponentName
from scrapy_rss.exceptions import NoNamespaceURIError


names = ['name', 'sub_name', 'имя']
empty_ns_prefixes = [None, '']
ns_prefixes = ['ns_prefix', 'pre_prefix', 'префикс']
empty_ns_uris = [None, '']
ns_uris = ['id1', 'http://path.to/somewhere']


@pytest.mark.parametrize("ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(empty_ns_prefixes, empty_ns_prefixes, ns_uris)))
def test_ns_prefix_property_setter_v1(ns_prefix, sec_ns_prefix, ns_uri):
    c = BaseNSComponent(ns_prefix=ns_prefix, ns_uri=ns_uri)
    c.ns_prefix = sec_ns_prefix
    assert c.ns_prefix == sec_ns_prefix


@pytest.mark.parametrize("ns_prefix,sec_ns_prefix,ns_uri",
                         ((ns_prefix, sec_ns_prefix, ns_uri)
                          for ns_prefix, sec_ns_prefix in combinations(ns_prefixes, 2)
                          for ns_uri in  ns_uris))
def test_ns_prefix_property_setter_v2(ns_prefix, sec_ns_prefix, ns_uri):
    c = BaseNSComponent(ns_prefix=ns_prefix, ns_uri=ns_uri)
    with pytest.raises(ValueError, match=r"already non-empty"):
        c.ns_prefix = sec_ns_prefix


@pytest.mark.parametrize("ns_prefix,sec_ns_prefix,ns_uri",
                         product(empty_ns_prefixes, ns_prefixes, empty_ns_uris))
def test_ns_prefix_property_setter_v3(ns_prefix, sec_ns_prefix, ns_uri):
    c = BaseNSComponent(ns_prefix=ns_prefix, ns_uri=ns_uri)
    with pytest.raises(NoNamespaceURIError, match=r"no namespace URI"):
        c.ns_prefix = sec_ns_prefix


@pytest.mark.parametrize("ns_prefix,ns_uri,sec_ns_uri",
                         chain(product(empty_ns_prefixes, empty_ns_uris, ns_uris),
                               product(empty_ns_prefixes, empty_ns_uris, empty_ns_uris)))
def test_ns_uri_property_setter_v1(ns_prefix, ns_uri, sec_ns_uri):
    c = BaseNSComponent(ns_prefix=ns_prefix, ns_uri=ns_uri)
    c.ns_uri = sec_ns_uri
    assert c.ns_uri == sec_ns_uri


@pytest.mark.parametrize("ns_prefix,ns_uri,sec_ns_uri",
                         ((ns_prefix, ns_uri, sec_ns_uri)
                          for ns_prefix in ns_prefixes
                          for ns_uri, sec_ns_uri in  combinations(ns_uris, 2)))
def test_ns_uri_property_setter_v2(ns_prefix, ns_uri, sec_ns_uri):
    c = BaseNSComponent(ns_prefix=ns_prefix, ns_uri=ns_uri)
    with pytest.raises(ValueError, match=r"already non-empty"):
        c.ns_uri = sec_ns_uri




@pytest.mark.parametrize("name,ns_prefix,ns_uri", product(names, empty_ns_prefixes, empty_ns_uris))
def test_init_name_only(name, ns_prefix, ns_uri):
    NSComponentName(name)
    NSComponentName(name, ns_prefix)
    NSComponentName(name, ns_prefix=ns_prefix)
    NSComponentName(name, ns_uri=ns_uri)
    NSComponentName(name, ns_prefix, ns_uri)
    NSComponentName(name, ns_prefix=ns_prefix)
    NSComponentName(name, ns_prefix=ns_prefix, ns_uri=ns_uri)


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         product(names, empty_ns_prefixes, ns_prefixes, empty_ns_uris))
def test_init_compound_name_only(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    with pytest.raises(NoNamespaceURIError, match=re.escape(sec_ns_prefix)):
        NSComponentName(compound_name)
    with pytest.raises(NoNamespaceURIError, match=re.escape(sec_ns_prefix)):
        NSComponentName(compound_name, ns_prefix)
    with pytest.raises(NoNamespaceURIError, match=re.escape(sec_ns_prefix)):
        NSComponentName(compound_name, ns_prefix=ns_prefix)
    with pytest.raises(NoNamespaceURIError, match=re.escape(sec_ns_prefix)):
        NSComponentName(compound_name, ns_uri=ns_uri)
    with pytest.raises(NoNamespaceURIError, match=re.escape(sec_ns_prefix)):
        NSComponentName(compound_name, ns_prefix, ns_uri)
    with pytest.raises(NoNamespaceURIError, match=re.escape(sec_ns_prefix)):
        NSComponentName(compound_name, ns_prefix=ns_prefix)
    with pytest.raises(NoNamespaceURIError, match=re.escape(sec_ns_prefix)):
        NSComponentName(compound_name, ns_prefix=ns_prefix, ns_uri=ns_uri)


@pytest.mark.parametrize("name,ns_prefix,ns_uri", product(names, ns_prefixes, empty_ns_uris))
def test_init_name_and_prefix_only(name, ns_prefix, ns_uri):
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(name, ns_prefix)
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(name, ns_prefix=ns_prefix)
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(name, ns_prefix, ns_uri)
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(name, ns_prefix, ns_uri=ns_uri)


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri", product(names, ns_prefixes, ns_prefixes, empty_ns_uris))
def test_init_compound_name_and_prefix_only(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(compound_name, ns_prefix)
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(compound_name, ns_prefix=ns_prefix)
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(compound_name, ns_prefix, ns_uri)
    with pytest.raises(NoNamespaceURIError, match=re.escape(ns_prefix)):
        NSComponentName(compound_name, ns_prefix, ns_uri=ns_uri)



@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_init_name_prefix_uri(name, ns_prefix, ns_uri):
    NSComponentName(name, ns_uri=ns_uri)
    NSComponentName(name, ns_prefix, ns_uri)
    NSComponentName(name, ns_prefix=ns_prefix, ns_uri=ns_uri)


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_init_compound_name_prefix_uri(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    NSComponentName(compound_name, ns_uri=ns_uri)
    NSComponentName(compound_name, ns_prefix, ns_uri)
    NSComponentName(compound_name, ns_prefix=ns_prefix, ns_uri=ns_uri)


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, empty_ns_uris),
                                                        product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_name_property(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    assert n.name == name
    n = NSComponentName(name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.name == name

@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_name_property_with_compound_name(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert n.name == name
    n = NSComponentName(compound_name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.name == name


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, empty_ns_uris),
                                                        product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_xml_name_property(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    assert n.xml_name == (ns_uri or '', name)
    n = NSComponentName(name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.xml_name == (ns_uri or '', name)


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_xml_name_property_with_compound_name(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert n.xml_name == (ns_uri or '', name)
    n = NSComponentName(compound_name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.xml_name == (ns_uri or '', name)


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, empty_ns_uris),
                                                        product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_pub_name_property(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    assert n.pub_name == name
    n = NSComponentName(name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.pub_name == name


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_pub_name_property_with_compound_name(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert n.pub_name == compound_name
    n = NSComponentName(compound_name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.pub_name == compound_name


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, empty_ns_uris),
                                                        product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_str(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    assert str(n) == name
    n = NSComponentName(name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert str(n) == name


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_str_with_compound_name(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert str(n) == compound_name
    n = NSComponentName(compound_name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert str(n) == compound_name


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, empty_ns_uris),
                                                        product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_priv_name_property(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    assert n.priv_name == '__' + name
    n = NSComponentName(name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.priv_name == '__' + name


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_priv_name_property_with_compound_name(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert n.priv_name == '__' + compound_name
    n = NSComponentName(compound_name, ns_prefix=ns_prefix, ns_uri=ns_uri)
    assert n.priv_name == '__' + compound_name


@pytest.mark.parametrize("name,ns_prefix,ns_uri", product(names, empty_ns_prefixes, empty_ns_uris))
def test_implemented_comparison_v1(name, ns_prefix, ns_uri):
    n1 = NSComponentName(name, ns_prefix, ns_uri)
    n2 = NSComponentName(name, ns_uri=ns_uri, ns_prefix=ns_prefix)
    n3 = NSComponentName(name + '9', ns_prefix, ns_uri)
    assert n1 == n2
    assert n2 == n1
    assert n1 != n3
    assert n3 != n1
    assert n2 != n3
    assert n3 != n2


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_comparison_v2(name, ns_prefix, ns_uri):
    n1 = NSComponentName(name, ns_prefix, ns_uri)
    n2 = NSComponentName(name, ns_uri=ns_uri, ns_prefix=ns_prefix)
    n3 = NSComponentName(name + '9', ns_prefix, ns_uri)
    n4 = NSComponentName(name, ns_prefix, ns_uri + '2')
    assert n1 == n2
    assert n2 == n1
    assert n1 != n3
    assert n3 != n1
    assert n2 != n3
    assert n3 != n2
    assert n1 != n4
    assert n4 != n1
    assert n2 != n4
    assert n4 != n2
    assert n3 != n4
    assert n4 != n3


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_comparison_with_compound_name(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n1 = NSComponentName(compound_name, ns_prefix, ns_uri)
    n2 = NSComponentName(compound_name, ns_uri=ns_uri, ns_prefix=ns_prefix)
    n3 = NSComponentName(compound_name + '9', ns_prefix, ns_uri)
    n4 = NSComponentName(compound_name, ns_prefix, ns_uri + '2')
    assert n1 == n2
    assert n2 == n1
    assert n1 != n3
    assert n3 != n1
    assert n2 != n3
    assert n3 != n2
    assert n1 != n4
    assert n4 != n1
    assert n2 != n4
    assert n4 != n2
    assert n3 != n4
    assert n4 != n3


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, empty_ns_uris),
                                                        product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_unsupported_comparison(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    with pytest.raises(NotImplementedError):
        n == (ns_uri, name)
    with pytest.raises(NotImplementedError):
        (ns_uri, name) == n
    with pytest.raises(NotImplementedError):
        n.pub_name == n
    with pytest.raises(NotImplementedError):
        n == n.pub_name


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         chain(product(names, empty_ns_prefixes, ns_prefixes, ns_uris),
                               product(names, ns_prefixes, ns_prefixes, ns_uris)))
def test_unsupported_comparison_with_compound_name(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    with pytest.raises(NotImplementedError):
        n == (ns_uri, name)
    with pytest.raises(NotImplementedError):
        (ns_uri, name) == n
    with pytest.raises(NotImplementedError):
        n.pub_name == n
    with pytest.raises(NotImplementedError):
        n == n.pub_name


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, empty_ns_uris),
                                                        product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_repr(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    assert repr(n) == "NSComponentName(name={!r}, ns_prefix={!r}, ns_uri={!r})".format(name, ns_prefix or '', ns_uri or '')


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         product(names, empty_ns_prefixes, ns_prefixes, ns_uris))
def test_repr_with_compound_name_v1(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert repr(n) == "NSComponentName(name={!r}, ns_prefix={!r}, ns_uri={!r})".format(name, sec_ns_prefix, ns_uri)



@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         product(names, ns_prefixes, ns_prefixes, ns_uris))
def test_repr_with_compound_name_v2(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert repr(n) == "NSComponentName(name={!r}, ns_prefix={!r}, ns_uri={!r})".format(name, ns_prefix, ns_uri)


@pytest.mark.parametrize("name,ns_prefix,ns_uri", product(names, empty_ns_prefixes, empty_ns_uris))
def test_get_namespaces_v1(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    namespaces = n.get_namespaces()
    assert isinstance(namespaces, set)
    assert namespaces == set()


@pytest.mark.parametrize("name,ns_prefix,ns_uri", chain(product(names, empty_ns_prefixes, ns_uris),
                                                        product(names, ns_prefixes, ns_uris)))
def test_get_namespaces_v2(name, ns_prefix, ns_uri):
    n = NSComponentName(name, ns_prefix, ns_uri)
    assert n.get_namespaces() == {(ns_prefix or '', ns_uri)}


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         product(names, empty_ns_prefixes, ns_prefixes, ns_uris))
def test_get_namespaces_with_compound_name_v1(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert n.get_namespaces() == {(sec_ns_prefix, ns_uri)}


@pytest.mark.parametrize("name,ns_prefix,sec_ns_prefix,ns_uri",
                         product(names, ns_prefixes, ns_prefixes, ns_uris))
def test_get_namespaces_with_compound_name_v2(name, ns_prefix, sec_ns_prefix, ns_uri):
    compound_name = sec_ns_prefix + '__' + name
    n = NSComponentName(compound_name, ns_prefix, ns_uri)
    assert n.get_namespaces() == {(ns_prefix, ns_uri)}


if __name__ == '__main__':
    pytest.main()
