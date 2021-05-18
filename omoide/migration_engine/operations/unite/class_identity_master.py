# -*- coding: utf-8 -*-
"""Helper class that is created to work with variables in source files.
"""
from functools import partial
from typing import Dict, Set, Tuple

from omoide import constants
from omoide.migration_engine.operations \
    .unite.class_uuid_master import UUIDMaster

__all__ = [
    'IdentityMaster',
]

ByNamespaceType = Dict[Tuple[str, str, str, str], str]


class IdentityMaster:
    """Helper class that is created to work with variables in source files."""

    def __init__(self) -> None:
        """Initialize instance."""
        self._cache: Dict[str, str] = {}

        self._prefix_to_method = {
            constants.PREFIX_THEME: 'generate_uuid_theme',
            constants.PREFIX_SYNONYM: 'generate_uuid_synonym',
            constants.PREFIX_GROUP: 'generate_uuid_group',
            constants.PREFIX_META: 'generate_uuid_meta',
        }

        self._already_generated: Set[str] = set()
        self._by_namespace: ByNamespaceType = {}

    def generate_value(self, branch: str, leaf: str,
                       uuid_type: str, variable: str,
                       uuid_master: UUIDMaster) -> str:
        """Create and store new uuid."""
        previous_value = self._cache.get(variable)

        if previous_value is not None:
            return previous_value

        if uuid_type not in constants.ALL_PREFIXES_SET:
            raise ValueError(
                f'Unknown uuid type {uuid_type!r} for variable {variable}'
            )

        generator = getattr(uuid_master, self._prefix_to_method[uuid_type])
        value = generator()

        self._store(branch, leaf, uuid_type, variable, value)

        return value

    def get_value(self, variable_name: str) -> str:
        """Get value by given name."""
        return self._cache[variable_name]

    def extract_variables(self, branch: str,
                          leaf: str) -> Dict[str, Dict[str, str]]:
        """Serialize to a dictionary.

        Note that we're avoiding adding static data here.
        """
        selector = partial(self.select_by_branch, branch, leaf)
        return {
            'themes': selector(constants.PREFIX_THEME, self._by_namespace),
            'synonyms': selector(constants.PREFIX_SYNONYM, self._by_namespace),
            'groups': selector(constants.PREFIX_GROUP, self._by_namespace),
            'metas': selector(constants.PREFIX_META, self._by_namespace),
        }

    @staticmethod
    def select_by_branch(target_branch: str, target_leaf: str,
                         target_uuid_type: str, storage: ByNamespaceType
                         ) -> Dict[str, str]:
        """Select only variables of given branch/leaf"""
        return {
            name: value
            for (branch, leaf, uuid_type, name), value in storage.items()
            if all([branch == target_branch,
                    leaf == target_leaf,
                    uuid_type == target_uuid_type])
        }

    def add_variable(self, branch: str, leaf: str,
                     uuid_type: str, variable: str, value: str) -> None:
        """Add external variable to the storage."""
        if uuid_type not in constants.ALL_PREFIXES_SET:
            raise ValueError(
                f'Unknown uuid type {uuid_type!r} for variable {variable!r}'
            )

        if value.startswith(constants.VARIABLE_SIGN):
            raise ValueError(
                f'Variable {variable!r} should '
                f'contain actual value, not {value!r}'
            )

        self._store(branch, leaf, uuid_type, variable, value)

    def _store(self, branch: str, leaf: str,
               uuid_type: str, name: str, value: str) -> None:
        """Add value to inner storages."""
        self._cache[name] = value
        self._by_namespace[(branch, leaf, uuid_type, name)] = value
