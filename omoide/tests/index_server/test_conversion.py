# -*- coding: utf-8 -*-

"""Tests.
"""
import pytest

from omoide.index_server import conversion


@pytest.mark.parametrize('seconds, reference', [
    (0, '0s'),
    (1, '1s'),
    (60, '1m'),
    (100, '1m 40s'),
    (900, '15m'),
    (2_760, '46m'),
    (86_400, '1d'),
    (99_658, '1d 3h 40m 58s'),
])
def test_format_as_human_readable_time(seconds, reference):
    assert conversion.human_readable_time(seconds) == reference
