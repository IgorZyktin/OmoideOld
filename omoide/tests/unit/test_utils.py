# -*- coding: utf-8 -*-

"""Tests.
"""
from omoide import utils


def test_byte_count_to_text_ru():
    """Must convert to readable size in russian."""
    func = utils.byte_count_to_text
    assert func(-2_000, language='RU') == '-2.0 КиБ'
    assert func(-2_048, language='RU') == '-2.0 КиБ'
    assert func(0, language='RU') == '0 Б'
    assert func(27, language='RU') == '27 Б'
    assert func(999, language='RU') == '999 Б'
    assert func(1_000, language='RU') == '1000 Б'
    assert func(1_023, language='RU') == '1023 Б'
    assert func(1_024, language='RU') == '1.0 КиБ'
    assert func(1_728, language='RU') == '1.7 КиБ'
    assert func(110_592, language='RU') == '108.0 КиБ'
    assert func(1_000_000, language='RU') == '976.6 КиБ'
    assert func(7_077_888, language='RU') == '6.8 МиБ'
    assert func(452_984_832, language='RU') == '432.0 МиБ'
    assert func(1_000_000_000, language='RU') == '953.7 МиБ'
    assert func(28_991_029_248, language='RU') == '27.0 ГиБ'
    assert func(1_855_425_871_872, language='RU') == '1.7 ТиБ'
    assert func(9_223_372_036_854_775_807, language='RU') == '8.0 ЭиБ'


def test_byte_count_to_text_en():
    """Must convert to readable size in english."""
    func = utils.byte_count_to_text
    assert func(-2_000, language='EN') == '-2.0 KiB'
    assert func(-2_048, language='EN') == '-2.0 KiB'
    assert func(0, language='EN') == '0 B'
    assert func(27, language='EN') == '27 B'
    assert func(999, language='EN') == '999 B'
    assert func(1_000, language='EN') == '1000 B'
    assert func(1_023, language='EN') == '1023 B'
    assert func(1_024, language='EN') == '1.0 KiB'
    assert func(1_728, language='EN') == '1.7 KiB'
    assert func(110_592, language='EN') == '108.0 KiB'
    assert func(1_000_000, language='EN') == '976.6 KiB'
    assert func(7_077_888, language='EN') == '6.8 MiB'
    assert func(452_984_832, language='EN') == '432.0 MiB'
    assert func(1_000_000_000, language='EN') == '953.7 MiB'
    assert func(28_991_029_248, language='EN') == '27.0 GiB'
    assert func(1_855_425_871_872, language='EN') == '1.7 TiB'
    assert func(9_223_372_036_854_775_807, language='EN') == '8.0 EiB'


def test_sep_digits():
    """Must separate digits on 1000s."""
    func = utils.sep_digits
    assert func('12345678') == '12345678'
    assert func(12345678) == '12 345 678'
    assert func(1234.5678) == '1 234.57'
    assert func(1234.5678, precision=4) == '1 234.5678'
    assert func(1234.0, precision=4) == '1 234.0000'
    assert func(1234.0, precision=0) == '1 234'
