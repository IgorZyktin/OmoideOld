# -*- coding: utf-8 -*-

"""Tests.
"""
from omoide.index_server import search_engine


def test_index_server_query(fix_query):
    # arrange
    query = fix_query
    query.and_ = ['animal']
    query.or_ = ['small']
    query.not_ = ['big']
    query.themes = ['animal']  # using tag as a theme
    ref_string = ("Query(and_=['animal'], or_=['small'], "
                  "not_=['big'], page=1, items_per_page=4, "
                  "themes=['animal'])")
    # assert
    assert len(query) == 3
    assert repr(query) == ref_string
    assert str(query) == ref_string


def test_index_server_meta_equality():
    # arrange
    meta1 = search_engine.ShallowMeta('u1', 1, '')
    meta2 = search_engine.ShallowMeta('u1', 1, '')
    meta3 = search_engine.ShallowMeta('u3', 1, '')

    # assert
    assert meta1 == meta2
    assert meta2 != meta3
    assert hash(meta1) == hash(meta2)
    assert hash(meta2) != hash(meta3)
