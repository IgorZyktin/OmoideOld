# -*- coding: utf-8 -*-

"""Handler for browser queries (not user search).
"""

from typing import Dict

__all__ = [
    'WebQuery',
]


class WebQuery:
    """Handler for browser queries (not user search).
    """

    def __init__(self, kwargs: Dict[str, str]) -> None:
        """Initialize instance."""
        self.kwargs = kwargs

    def __str__(self) -> str:
        """Return textual representation."""
        components = []

        for key, value in self.kwargs.items():
            components.append(f'{key}={value}')

        string = '?' + '&'.join(components)
        string = string.replace(' ', '%20')
        string = string.replace(',', '%2C')
        string = string.replace('+', '%2B')

        return string

    def __setitem__(self, key: str, value: str) -> None:
        """Change one of the kwargs."""
        self.kwargs[key] = value

    @classmethod
    def from_request(cls, request_args: dict, **kwargs: str) -> 'WebQuery':
        """Build query from original request."""
        # avoiding multikey parameter passing
        request_args = dict(request_args)

        request_args.update(kwargs)
        return cls(request_args)

    def replace(self, **kwargs) -> 'WebQuery':
        """Create new instance with given kwargs."""
        cls = type(self)
        return cls({**self.kwargs, **kwargs})

    def get(self, key: str, default: str = '') -> str:
        """Return value of a parameter."""
        return self.kwargs.get(key, default)
