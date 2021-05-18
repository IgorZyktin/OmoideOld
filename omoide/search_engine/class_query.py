# -*- coding: utf-8 -*-

"""Fully processed user search request.
"""
from itertools import chain
from typing import Collection, Dict, List, FrozenSet, Tuple

from omoide import constants


class Query:
    """Fully processed user search request."""

    def __init__(self,
                 and_: Collection[str],
                 or_: Collection[str],
                 not_: Collection[str],
                 sequence: List[Tuple[str, str]]) -> None:
        """Initialize instance."""
        self.and_: FrozenSet[str] = frozenset(and_)
        self.or_: FrozenSet[str] = frozenset(or_)
        self.not_: FrozenSet[str] = frozenset(not_)
        self.sequence: Tuple[Tuple[str, str], ...] = tuple(sequence)

    def __str__(self) -> str:
        """Reconstruct query from known arguments."""
        keywords = chain.from_iterable(self.as_keywords().values())
        return ' '.join(keywords)

    def __repr__(self) -> str:
        """Return textual representation."""
        return f'<{type(self).__name__}, n={self.total_items()}>'

    def __bool__(self) -> bool:
        """Return True if query has actual words to search."""
        return bool(self.and_ or self.or_ or self.not_)

    def append_and(self, *new_values: str) -> 'Query':
        """Add some values to the and_ field."""
        return self._append_generic(*new_values, attribute='and_')

    def append_or(self, *new_values: str) -> 'Query':
        """Add some values to the or_ field."""
        return self._append_generic(*new_values, attribute='or_')

    def append_not(self, *new_values: str) -> 'Query':
        """Add some values to the not_ field."""
        return self._append_generic(*new_values, attribute='not_')

    def _append_generic(self, *new_values: str,
                        attribute: str) -> 'Query':
        """Add some values to the and_ field."""
        values = self.as_dict()
        values[attribute] += list(new_values)
        cls = type(self)

        if attribute == 'and_':
            operator = 'and'
        elif attribute == 'or_':
            operator = 'or'
        else:
            operator = 'not'

        sequence = list(self.sequence) + [(operator, x) for x in new_values]

        return cls(**values, sequence=sequence)

    def total_items(self) -> int:
        """Return total amount of registered items."""
        return len(self.and_) + len(self.or_) + len(self.not_)

    def as_keywords(self) -> Dict[str, List[str]]:
        """Return sorted collection of internal keywords."""
        pairs = self.as_keyword_pais()

        def stringify_pair(pair: Tuple[str, str]) -> str:
            """Convert operator-word pair into string."""
            return f'{pair[0]} {pair[1]}'

        return {
            key: [stringify_pair(pair) for pair in value]
            for key, value in pairs.items()
        }

    def as_keyword_pais(self) -> Dict[str, List[Tuple[str, str]]]:
        """Return sorted collection of internal keywords, machine readable."""

        def as_pair(attribute: str,
                    collection: FrozenSet[str]) -> List[Tuple[str, str]]:
            """Shorthand construction."""
            value = getattr(constants, attribute)
            return [(value, x) for x in sorted(collection)]

        return {'and_': as_pair('KW_AND', self.and_),
                'or_': as_pair('KW_OR', self.or_),
                'not_': as_pair('KW_NOT', self.not_)}

    def as_dict(self) -> Dict[str, List[str]]:
        """Return representation of the query as a dict."""
        return {'and_': sorted(self.and_),
                'or_': sorted(self.or_),
                'not_': sorted(self.not_)}
