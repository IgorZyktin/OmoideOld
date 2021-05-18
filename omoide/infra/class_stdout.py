# -*- coding: utf-8 -*-

"""Abstraction of printing.
"""
from colorama import init, Fore

init()

__all__ = [
    'STDOut',
]


class STDOut:
    """Abstraction of printing.
    """

    @classmethod
    def print(cls, text: str, *args, **kwargs) -> None:
        """Just print, no fancy colors."""
        kwargs['end'] = kwargs.get('end', '\n')
        return cls.extended_print('', text, *args, **kwargs)

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
