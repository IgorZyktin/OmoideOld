# -*- coding: utf-8 -*-
"""Helper type that tracks changes.
"""

from pydantic import BaseModel, Field

from omoide import infra
from omoide.constants import storage as storage_const
from omoide.infra import walking

__all__ = [
    'UniteTrace',
    'MakeMigrationsTrace',
    'MakeRelocationsTrace',
    'MigrateTrace',
    'RelocateTrace',
    'SyncTrace',
    'FreezeTrace',
    'Passport',
]


class BaseTrace(BaseModel):
    """Generic step metainfo.
    """
    last_update: str = ''
    revision: str = ''


class TraceWithFingerprints(BaseTrace):
    """Trace that mainly focus on files.
    """
    fingerprints: infra.Fingerprints = Field(default_factory=dict)


class UniteTrace(TraceWithFingerprints):
    """Unite step metainfo.
    """


class MakeMigrationsTrace(TraceWithFingerprints):
    """MakeMigrations step metainfo.
    """


class MakeRelocationsTrace(BaseTrace):
    """MakeRelocations step metainfo.
    """


class MigrateTrace(BaseTrace):
    """Migrate step metainfo.
    """


class RelocateTrace(BaseTrace):
    """Relocate step metainfo.
    """


class SyncTrace(BaseTrace):
    """Sync step metainfo.
    """


class FreezeTrace(BaseTrace):
    """Freeze step metainfo.
    """


class Passport(BaseModel):
    """Helper type that tracks changes.
    """
    last_update: str = ''
    unite: UniteTrace = Field(default=UniteTrace())
    make_migrations: MakeMigrationsTrace = Field(
        default=MakeMigrationsTrace())
    make_relocations: MakeRelocationsTrace = Field(
        default=MakeRelocationsTrace())
    migrate: MigrateTrace = Field(default=MigrateTrace())
    relocate: RelocateTrace = Field(default=RelocateTrace())
    sync: SyncTrace = Field(default=SyncTrace())
    freeze: FreezeTrace = Field(default=FreezeTrace())

    @staticmethod
    def already_processed(bottom: walking.Bottom,
                          path: str, storage: infra.Fingerprints) -> bool:
        """Return True if unite file is already processed."""
        key = f'{bottom.branch}_{bottom.leaf}'
        fingerprint = bottom.filesystem.get_fingerprint(path)
        return fingerprint == storage.get(key)

    def register_unite(self, bottom: walking.Bottom, path: str
                       ) -> infra.Fingerprint:
        """Save changes."""
        self._register_action(self.unite, bottom)
        key = f'{bottom.branch}_{bottom.leaf}'
        fingerprint = bottom.filesystem.get_fingerprint(path)
        self.unite.fingerprints[key] = fingerprint
        return fingerprint

    def register_make_migrations(self, bottom: walking.Bottom,
                                 path: str) -> infra.Fingerprint:
        """Save changes."""
        self._register_action(self.make_migrations, bottom)
        key = f'{bottom.branch}_{bottom.leaf}'
        fingerprint = bottom.filesystem.get_fingerprint(path)
        self.make_migrations.fingerprints[key] = fingerprint
        return fingerprint

    def _register_action(self, component: BaseTrace,
                         bottom: walking.Bottom) -> None:
        """Generic registration method."""
        self.last_update = bottom.last_update
        component.last_update = bottom.last_update
        component.revision = bottom.revision

    def save_to_file(self, bottom: walking.Bottom) -> str:
        """Save Passport instance to file."""
        path = bottom.filesystem.join(
            bottom.root_folder,
            storage_const.STORAGE_FOLDER_NAME,
            bottom.branch,
            bottom.leaf,
            storage_const.PASSPORT_FILE_NAME,
        )

        bottom.filesystem.write_json(
            bottom.filesystem.absolute(path),
            self.dict(),
        )
        return path


def load_from_file(bottom: walking.Bottom) -> Passport:
    """Load Passport instance from file."""
    path = bottom.filesystem.join(
        bottom.root_folder,
        storage_const.STORAGE_FOLDER_NAME,
        bottom.branch,
        bottom.leaf,
        storage_const.PASSPORT_FILE_NAME,
    )

    try:
        contents = bottom.filesystem.read_json(
            bottom.filesystem.absolute(path)
        )
        passport = Passport(**contents)
    except FileNotFoundError:
        passport = Passport()

    return passport
