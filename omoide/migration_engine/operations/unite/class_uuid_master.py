# -*- coding: utf-8 -*-

"""Special class that handles UUID generation.
"""
import uuid as uuid_module
from collections import defaultdict
from typing import Collection, Optional, List, Sequence, NoReturn

from omoide import constants

__all__ = [
    'UUIDMaster',
]


class UUIDMaster:
    """Special class that handles UUID generation."""

    def __init__(self, all_uuids: Optional[Collection[str]] = None) -> None:
        """Initialize instance."""
        self._all_uuids = set(all_uuids) if all_uuids is not None else set()
        self._given_queue: List[str] = []
        self._used_uuids: List[str] = []

    def __contains__(self, uuid: str) -> bool:
        """Return True if this UUID is already used."""
        return uuid in self._all_uuids

    def extract_used_uuids(self) -> List[str]:
        """Return copy of used uuids."""
        result = self._used_uuids.copy()
        self._used_uuids.clear()
        return result

    def ensure_that_uuid_is_unique(self, uuid: str) -> Optional[NoReturn]:
        """Raise it this UUID is duplicated."""
        if uuid in self._all_uuids:
            raise ValueError(
                f'Seems like same UUID was generated twice: {uuid}'
            )

    def ensure_that_queue_is_unique(self) -> Optional[NoReturn]:
        """Check our queue for uniqueness."""
        all_uuids = defaultdict(int)

        for original in self._given_queue:
            all_uuids[original] += 1
            if all_uuids[original] > 1:
                raise ValueError('Seems like same UUID was added '
                                 f'to the queue twice: {original}')

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
        if self._given_queue:
            uuid = self._given_queue.pop()
        else:
            uuid = self.generate_uuid()

        self.ensure_that_uuid_is_unique(uuid)
        self._all_uuids.add(uuid)
        self._used_uuids.append(uuid)
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

    def insert_queue(self, uuids: Sequence[str]) -> None:
        """Add uuids queue."""
        self._given_queue = list(reversed(uuids))
        self.ensure_that_queue_is_unique()

    @staticmethod
    def get_prefix(string: str) -> str:
        """Return prefix of the UUID."""
        return string.split('_')[0]

    def add_existing_uuid(self, uuid: str) -> None:
        """Add this value to used ones (even if it is contained in queue)."""
        prefix = self.get_prefix(uuid)

        if prefix not in constants.ALL_PREFIXES_SET:
            raise ValueError(f'Unknown prefix {prefix!r} for uuid {uuid}')

        self._all_uuids.add(uuid)
