# -*- coding: utf-8 -*-

"""Helper class that stores query parameters.
"""
import re
from typing import TypeVar, Generic, Type, List, Dict, Set, Tuple

from omoide import constants
from omoide.utils import group_to_size

QueryType = TypeVar('QueryType')


class QueryBuilder(Generic[QueryType]):
    """Helper class that makes query instances.
    """
    string = '|'.join(r'\s\{}\s?'.format(x) for x in constants.OPERATORS)
    pattern = re.compile('(' + string + ')')

    search_map = {constants.KW_AND: 'and_',
                  constants.KW_OR: 'or_',
                  constants.KW_NOT: 'not_'}

    def __init__(self, target_type: Type[QueryType]) -> None:
        """Initialize instance."""
        self.target_type = target_type

    def split_request_into_parts(self, query_text: str) -> List[str]:
        """Turn user request into series of words."""
        # adding space to help regex
        parts = self.pattern.split(' ' + query_text)
        parts = [x.strip() for x in parts if x.strip()]

        if not parts:
            return []

        if parts[0] not in constants.OPERATORS:
            if len(parts) == 1:
                parts.insert(0, constants.KW_AND)
            else:
                parts.insert(0, constants.KW_OR)

        return parts

    def update_sets(self, operator: str, word: str,
                    sets: Dict[str, Set[str]]) -> None:
        """Put new words in the sets dictionary."""
        word = word.lower()
        target = self.search_map.get(operator, '')

        if target:
            sets[target].add(word)

    def from_query(self, query_text: str) -> QueryType:
        """Make instance representing given query."""
        sets = dict(and_=set(),
                    or_=set(),
                    not_=set())

        sequence: List[Tuple[str, str]] = []
        parts = self.split_request_into_parts(query_text)

        for operator, word in group_to_size(parts):
            self.update_sets(operator, word, sets)
            if operator == constants.KW_AND:
                _operator = 'and'
            elif operator == constants.KW_OR:
                _operator = 'or'
            else:
                _operator = 'not'
            sequence.append((_operator, word))

        return self.target_type(and_=set(sets['and_']),
                                or_=set(sets['or_']),
                                not_=set(sets['not_']),
                                sequence=sequence)
