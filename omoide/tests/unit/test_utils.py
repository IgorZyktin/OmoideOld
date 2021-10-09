# -*- coding: utf-8 -*-

"""Tests.
"""
import pytest

from omoide import utils


@pytest.mark.parametrize('size, reference', [
    (-2_000, '-2.0 КиБ'),
    (-2_048, '-2.0 КиБ'),
    (0, '0 Б'),
    (27, '27 Б'),
    (999, '999 Б'),
    (1_000, '1000 Б'),
    (1_023, '1023 Б'),
    (1_024, '1.0 КиБ'),
    (1_728, '1.7 КиБ'),
    (110_592, '108.0 КиБ'),
    (1_000_000, '976.6 КиБ'),
    (7_077_888, '6.8 МиБ'),
    (452_984_832, '432.0 МиБ'),
    (1_000_000_000, '953.7 МиБ'),
    (28_991_029_248, '27.0 ГиБ'),
    (1_855_425_871_872, '1.7 ТиБ'),
    (9_223_372_036_854_775_807, '8.0 ЭиБ'),
])
def test_byte_count_to_text_ru(size, reference):
    """Must convert to readable size in russian."""
    assert utils.byte_count_to_text(size, language='RU') == reference


@pytest.mark.parametrize('size, reference', [
    (-2_000, '-2.0 KiB'),
    (-2_048, '-2.0 KiB'),
    (0, '0 B'),
    (27, '27 B'),
    (999, '999 B'),
    (1_000, '1000 B'),
    (1_023, '1023 B'),
    (1_024, '1.0 KiB'),
    (1_728, '1.7 KiB'),
    (110_592, '108.0 KiB'),
    (1_000_000, '976.6 KiB'),
    (7_077_888, '6.8 MiB'),
    (452_984_832, '432.0 MiB'),
    (1_000_000_000, '953.7 MiB'),
    (28_991_029_248, '27.0 GiB'),
    (1_855_425_871_872, '1.7 TiB'),
    (9_223_372_036_854_775_807, '8.0 EiB'),
])
def test_byte_count_to_text_en(size, reference):
    """Must convert to readable size in english."""
    assert utils.byte_count_to_text(size, language='EN') == reference


def test_sep_digits():
    """Must separate digits on 1000s."""
    assert utils.sep_digits('12345678') == '12345678'
    assert utils.sep_digits(12345678) == '12 345 678'
    assert utils.sep_digits(1234.5678) == '1 234.57'
    assert utils.sep_digits(1234.5678, precision=4) == '1 234.5678'
    assert utils.sep_digits(1234.0, precision=4) == '1 234.0000'
    assert utils.sep_digits(1234.0, precision=0) == '1 234'


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
    assert utils.human_readable_time(seconds) == reference
