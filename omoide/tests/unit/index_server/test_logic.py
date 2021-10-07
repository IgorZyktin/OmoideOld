# -*- coding: utf-8 -*-

"""Tests.
"""
from pympler.asizeof import asizeof

from omoide import utils
from omoide.index_server import logic


def test_logic_analyze_index(fix_index):
    # arrange
    index = fix_index

    # act
    result = logic.analyze_index(fix_index)

    # assert
    assert result == {
        'index_avg_bucket': 2.25,
        'index_buckets': 4,
        'index_max_bucket': 5,
        'index_min_bucket': 2,
        'index_records': 9,
        'index_size': utils.byte_count_to_text(asizeof(index))
    }


def test_logic_create_index(fix_index):
    raise


def test_logic_actually_load_from_database(fix_index):
    raise


def test_logic_get_engine():
    raise


def test_logic_index_pipeline():
    raise


def test_logic_reload():
    raise


def test_logic_format_status():
    raise


def test_logic_search():
    raise
