# -*- coding: utf-8 -*-

"""Special class that handles UUID generation.
"""
import uuid as uuid_module
from typing import Collection, Optional, NoReturn

from omoide import constants

__all__ = [
    'UUIDMaster',
]


class UUIDMaster:
    """Special class that handles UUID generation."""

    def __init__(self, all_uuids: Optional[Collection[str]] = None) -> None:
        """Initialize instance."""
        self._all_uuids = set(all_uuids) if all_uuids is not None else set()

    def __contains__(self, uuid: str) -> bool:
        """Return True if this UUID is already used."""
        return uuid in self._all_uuids

    def ensure_that_uuid_is_unique(self, uuid: str) -> Optional[NoReturn]:
        """Raise it this UUID is duplicated."""
        if uuid in self._all_uuids:
            raise ValueError(
                f'Seems like same UUID was generated twice: {uuid}'
            )

    @staticmethod
    def _generate_uuid4() -> str:
        """Generate basic UUID4."""
        return str(uuid_module.uuid4())

    def generate_uuid(self) -> str:
        """Create new UUID."""
        uuid = self._generate_uuid4()
        while uuid in self._all_uuids:
            uuid = self._generate_uuid4()
        return uuid

    def generate_and_add_uuid(self, prefix: str) -> str:
        """Create and add new UUID."""
        uuid = self.generate_uuid()
        self.ensure_that_uuid_is_unique(uuid)
        self._all_uuids.add(uuid)
        full_uuid = f'{prefix}_{uuid}'
        return full_uuid

    def generate_uuid_theme(self) -> str:
        """Create and add new UUID for theme."""
        return self.generate_and_add_uuid(prefix=constants.PREFIX_THEME)

    def generate_uuid_group(self) -> str:
        """Create and add new UUID for group."""
        return self.generate_and_add_uuid(prefix=constants.PREFIX_GROUP)

    def generate_uuid_meta(self) -> str:
        """Create and add new UUID for meta."""
        uuid = self.generate_and_add_uuid(prefix=constants.PREFIX_META)
        return uuid

    def generate_uuid_synonym(self) -> str:
        """Create and add new UUID for synonym."""
        return self.generate_and_add_uuid(prefix=constants.PREFIX_SYNONYM)

    @staticmethod
    def get_prefix(string: str) -> str:
        """Return prefix of the UUID."""
        return string.split('_')[0]

    def add_existing_uuids(self, *uuids: str) -> None:
        """Add this value to used ones (even if it is contained in queue)."""
        for uuid in uuids:
            prefix = self.get_prefix(uuid)

            if prefix not in constants.ALL_PREFIXES_SET:
                raise ValueError(f'Unknown prefix {prefix!r} for uuid {uuid}')

            self._all_uuids.add(uuid)
