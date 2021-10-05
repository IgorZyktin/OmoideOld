# -*- coding: utf-8 -*-

"""Fast search storage.
"""
from typing import List, FrozenSet, Dict

__all__ = [
    'ShallowMeta',
    'Index',
]


class ShallowMeta:
    """Typical metarecord, simplified form."""
    __slots__ = ('uuid', 'number', 'path_to_thumbnail')

    def __init__(self, uuid: str, number: int, path_to_thumbnail: str) -> None:
        """Initialize instance."""
        self.uuid = uuid
        self.number = number
        self.path_to_thumbnail = path_to_thumbnail

    def __eq__(self, other) -> bool:
        """Return True if object has same uuid."""
        return self.uuid == getattr(other, 'uuid', None)

    def __hash__(self) -> int:
        """Return hash of the uuid."""
        return hash(self.uuid)

    def dict(self) -> dict:
        """Convert item into dict."""
        return {
            'uuid': self.uuid,
            'path': self.path_to_thumbnail,
            'number': self.number,
        }


class Index:
    """Fast search storage.
    """

    def __init__(self, all_metas: List[ShallowMeta],
                 by_tags: Dict[str, FrozenSet[str]]) -> None:
        """Initialize instance."""
        self.all_metas = tuple(all_metas)
        self.all_uuids = frozenset(x.uuid for x in all_metas)
        self.by_tags = by_tags
        self.by_uuid = {meta.uuid: meta for meta in all_metas}

    def __len__(self) -> int:
        """Return total amount of records."""
        return len(self.all_metas)

    def get_by_tag(self, tag: str) -> frozenset[str]:
        """Return UUIDs corresponding to this tag."""
        return self.by_tags.get(tag, frozenset())
