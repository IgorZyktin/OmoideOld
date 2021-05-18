# -*- coding: utf-8 -*-
"""Helper type for a single SQL command representation.
"""
from typing import Optional

__all__ = [
    'SQL',
]


class SQL:
    """Helper type for a single SQL command representation.
    """

    def __init__(self, statement):
        """Initialize instance."""
        self.statement = statement
        self._cached_statement: Optional[str] = None

    def __str__(self) -> str:
        """Return textual representation."""
        if self._cached_statement is None:
            stmt = self.statement.compile(
                compile_kwargs={"literal_binds": True}
            )
            self._cached_statement = str(stmt)
        return self._cached_statement
