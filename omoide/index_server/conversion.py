# -*- coding: utf-8 -*-
"""Format changing utilities.
"""


def human_readable_time(
        seconds: int, *, _weeks: int = 0, _days: int = 0, _hours: int = 0,
        _minutes: int = 0, _seconds: int = 0,
        _suffixes: tuple[str, ...] = ('w', 'd', 'h', 'm', 's')) -> str:
    """Format interval as human readable description.

    >>> human_readable_time(46551387)
    '76w 6d 18h 56m 27s'
    """
    if seconds < 1:
        return '0s'

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
