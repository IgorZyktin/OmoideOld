# -*- coding: utf-8 -*-

"""Abstraction of printing.
"""
import math
from typing import Collection

from colorama import init, Fore

init()

__all__ = [
    'STDOut',
    'with_progress',
]


class STDOut:
    """Abstraction of printing.
    """

    @classmethod
    def print(cls, text: str, *args, prefix: str = '', **kwargs) -> None:
        """Just print, no fancy colors."""
        kwargs['end'] = kwargs.get('end', '\n')
        return cls.extended_print(prefix, text, *args, **kwargs)

    @classmethod
    def light_green(cls, text: str, *args, **kwargs) -> None:
        """Print light green."""
        return cls.extended_print(Fore.LIGHTGREEN_EX, text, *args, **kwargs)

    @classmethod
    def green(cls, text: str, *args, **kwargs) -> None:
        """Print green."""
        return cls.extended_print(Fore.GREEN, text, *args, **kwargs)

    @classmethod
    def yellow(cls, text: str, *args, **kwargs) -> None:
        """Print yellow."""
        return cls.extended_print(Fore.YELLOW, text, *args, **kwargs)

    @classmethod
    def red(cls, text: str, *args, **kwargs) -> None:
        """Print red."""
        return cls.extended_print(Fore.RED, text, *args, **kwargs)

    @classmethod
    def gray(cls, text: str, *args, **kwargs) -> None:
        """Print gray."""
        return cls.extended_print(Fore.LIGHTBLACK_EX, text, *args, **kwargs)

    @classmethod
    def magenta(cls, text: str, *args, **kwargs) -> None:
        """Print magenta."""
        return cls.extended_print(Fore.MAGENTA, text, *args, **kwargs)

    @classmethod
    def cyan(cls, text: str, *args, **kwargs) -> None:
        """Print cyan."""
        return cls.extended_print(Fore.CYAN, text, *args, **kwargs)

    @classmethod
    def extended_print(cls, prefix: str, text: str, *args, **kwargs) -> None:
        """Print with prefix (usually color)."""
        kwargs['end'] = kwargs.get('end', f'{Fore.RESET}\n')
        return print(prefix + text, *args, **kwargs)


def with_progress(iterable: Collection, stdout: STDOut, prefix: str = ''):
    """Iterate with progress bar."""
    sequence = list(iterable)
    total = len(sequence)
    bar_width = 65
    for i, element in enumerate(sequence, start=1):
        percent = i / total
        complete = math.ceil(bar_width * percent)
        left = bar_width - complete
        stdout.print('#' * complete + '_' * left + f' {percent:.1%}',
                     prefix='\r' + prefix, end='')
        yield element

    stdout.print('', prefix='\r', end='')
