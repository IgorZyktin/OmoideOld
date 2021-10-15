# -*- coding: utf-8 -*-
"""Helper type that tracks changes.
"""

from pydantic import BaseModel, Field

from omoide import commands
from omoide import infra
from omoide.constants import storage as storage_const

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
    fingerprints: dict[str, infra.Fingerprint] = Field(default_factory=dict)


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
    def already_processed(command: commands.FilesRelatedCommand,
                          path: str, filesystem: infra.Filesystem,
                          storage: dict[str, infra.Fingerprint]) -> bool:
        """Return True if unite file is already processed."""
        key = f'{command.branch}_{command.leaf}'
        fingerprint = filesystem.get_fingerprint(path)
        return fingerprint == storage.get(key)

    def register_unite(self, command: commands.FilesRelatedCommand,
                       branch: str, leaf: str, path: str,
                       filesystem: infra.Filesystem) -> None:
        """Save changes."""
        self._register_action(self.unite, command)
        key = f'{branch}_{leaf}'
        self.unite.fingerprints[key] = filesystem.get_fingerprint(path)

    def register_make_migrations(self, command: commands.FilesRelatedCommand,
                                 branch: str, leaf: str, path: str,
                                 filesystem: infra.Filesystem) -> None:
        """Save changes."""
        self._register_action(self.make_migrations, command)
        key = f'{branch}_{leaf}'
        self.make_migrations.fingerprints[key] \
            = filesystem.get_fingerprint(path)

    def _register_action(self, component: BaseTrace,
                         command: commands.FilesRelatedCommand) -> None:
        """Generic registration method."""
        self.last_update = command.now
        component.last_update = command.now
        component.revision = command.revision


def load_from_file(root: str, branch: str, leaf: str,
                   filesystem: infra.Filesystem) -> Passport:
    """Load Passport instance from file."""
    path = filesystem.join(root, storage_const.STORAGE_FOLDER_NAME,
                           branch, leaf, storage_const.PASSPORT_FILE_NAME)
    try:
        contents = filesystem.read_json(filesystem.absolute(path))
        passport = Passport(**contents)
    except FileNotFoundError:
        passport = Passport()

    return passport


def save_to_file(passport: Passport, root: str, branch: str, leaf: str,
                 filesystem: infra.Filesystem) -> str:
    """Save Passport instance to file."""
    path = filesystem.join(root, storage_const.STORAGE_FOLDER_NAME,
                           branch, leaf, storage_const.PASSPORT_FILE_NAME)
    filesystem.write_json(filesystem.absolute(path), passport.dict())
    return path
