# -*- coding: utf-8 -*-

"""Various unrelated functions.
"""
import datetime
from collections import defaultdict
from itertools import zip_longest
from typing import Collection, Iterable, Any, Iterator

SUFFIXES = {
    'RU': {'B': 'Б', 'kB': 'кБ', 'MB': 'МБ', 'GB': 'ГБ', 'TB': 'ТБ',
           'PB': 'ПБ', 'EB': 'ЭБ', 'KiB': 'КиБ', 'MiB': 'МиБ',
           'GiB': 'ГиБ', 'TiB': 'ТиБ', 'PiB': 'ПиБ', 'EiB': 'ЭиБ'},

    'EN': {'B': 'B', 'kB': 'kB', 'MB': 'MB', 'GB': 'GB', 'TB': 'TB',
           'PB': 'PB', 'EB': 'EB', 'KiB': 'KiB', 'MiB': 'MiB',
           'GiB': 'GiB', 'TiB': 'TiB', 'PiB': 'PiB', 'EiB': 'EiB'},
}


def byte_count_to_text(total_bytes: int | float, language: str = 'EN') -> str:
    """Convert amount of bytes into human readable format.

    >>> byte_count_to_text(1023)
    '1023 B'
    """
    total_bytes = int(total_bytes)

    prefix = ''
    if total_bytes < 0:
        prefix = '-'
        total_bytes = abs(total_bytes)

    if total_bytes < 1024:
        suffix = SUFFIXES[language]['B']
        return f'{prefix}{int(total_bytes)} {suffix}'

    total_bytes /= 1024

    if total_bytes < 1024:
        suffix = SUFFIXES[language]['KiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    total_bytes /= 1024

    if total_bytes < 1024:
        suffix = SUFFIXES[language]['MiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    total_bytes /= 1024

    if total_bytes < 1024:
        suffix = SUFFIXES[language]['GiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    total_bytes /= 1024

    if total_bytes < 1024:
        suffix = SUFFIXES[language]['TiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    suffix = SUFFIXES[language]['EiB']
    return f'{total_bytes / 1024 / 1024 :0.1f} {suffix}'


def sep_digits(number: int | float | str, precision: int = 2) -> str:
    """Return number as string with separated thousands.

    >>> sep_digits('12345678')
    '12345678'

    >>> sep_digits(12345678)
    '12 345 678'

    >>> sep_digits(1234.5678)
    '1 234.57'

    >>> sep_digits(1234.5678, precision=4)
    '1 234.5678'
    """
    if isinstance(number, int):
        result = '{:,}'.format(number).replace(',', ' ')

    elif isinstance(number, float):
        if precision == 0:
            int_value = int(round(number, precision))
            result = '{:,}'.format(int_value).replace(',', ' ')

        else:
            float_value = round(number, precision)
            result = '{:,}'.format(float_value).replace(',', ' ')

        if '.' in result:
            tail = result.rsplit('.', maxsplit=1)[-1]
            result += '0' * (precision - len(tail))

    else:
        result = str(number)

    return result


def arrange_by_alphabet(words: Collection[str],
                        unique: bool = True) -> dict[str, list[str]]:
    """Group words by first letter.

    >>> arrange_by_alphabet(['best', 'ant', 'art', '25'])
    {'2': ['25'], 'A': ['ant', 'art'], 'B': ['best']}
    """
    cleaned_words = [x.strip().lower() for x in words]
    sorted_words = sorted(x for x in cleaned_words if x)
    arranged_words = defaultdict(list)

    for word in sorted_words:
        first_letter = word[0].upper()
        arranged_words[first_letter].append(word)

    if unique:
        for key in arranged_words:
            arranged_words[key] = list(dict.fromkeys(arranged_words[key]))

    return dict(arranged_words)


def group_to_size(iterable: Iterable, group_size: int = 2,
                  default: Any = '?') -> Iterator[tuple]:
    """Return contents of the iterable grouped in blocks of given size.

    >>> list(group_to_size([1, 2, 3, 4, 5, 6, 7], 2, '?'))
    [(1, 2), (3, 4), (5, 6), (7, '?')]

    >>> list(group_to_size([1, 2, 3, 4, 5, 6, 7], 3, '?'))
    [(1, 2, 3), (4, 5, 6), (7, '?', '?')]
    """
    return zip_longest(*[iter(iterable)] * group_size, fillvalue=default)


def now() -> datetime.datetime:
    """Return current time."""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def human_readable_time(seconds: int) -> str:
    """Format interval as human readable description.

    >>> human_readable_time(46551387)
    '76w 6d 18h 56m 27s'

    >>> human_readable_time(600)
    '10m'
    """
    if seconds < 1:
        return '0s'

    _weeks = 0
    _days = 0
    _hours = 0
    _minutes = 0
    _seconds = 0
    _suffixes = ('w', 'd', 'h', 'm', 's')

    if seconds > 0:
        _minutes, _seconds = divmod(seconds, 60)
        _hours, _minutes = divmod(_minutes, 60)
        _days, _hours = divmod(_hours, 24)
        _weeks, _days = divmod(_days, 7)

    values = [_weeks, _days, _hours, _minutes, _seconds]
    string = ' '.join(
        f'{x}{_suffixes[i]}' for i, x in enumerate(values) if x
    )

    return string
