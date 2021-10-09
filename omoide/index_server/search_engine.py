# -*- coding: utf-8 -*-

"""Fast search storage.
"""

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
    """ShallowMeta storage that supports fast search.
    """

    def __init__(self,
                 all_metas: list[ShallowMeta],
                 by_tags: dict[str, frozenset[str]]) -> None:
        """Initialize instance."""
        self.all_metas_tuple = tuple(all_metas)
        self.all_metas_set = frozenset(all_metas)
        self.by_uuid = {meta.uuid: meta for meta in all_metas}
        self.by_tags: dict[str, frozenset[ShallowMeta]] = {}

        for tag, uuids in by_tags.items():
            self.by_tags[tag] = frozenset([self.by_uuid[uuid]
                                           for uuid in uuids])

    def __len__(self) -> int:
        """Return total amount of records."""
        return len(self.all_metas_tuple)

    def get_by_tag(self, tag: str) -> frozenset[ShallowMeta]:
        """Return UUIDs corresponding to this tag."""
        return self.by_tags.get(tag, frozenset())
