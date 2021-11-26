# -*- coding: utf-8 -*-

"""Data transfer objects for command line operations.
"""
from dataclasses import dataclass

__all__ = [
    'BaseCommand',
    'FilesRelatedCommand',
    'UniteCommand',
    'MakeRelocationsCommand',
    'MakeMigrationsCommand',
    'MigrateCommand',
    'RelocateCommand',
    'SyncCommand',
    'FreezeCommand',
    'ShowTreeCommand',
    'RSyncCommand',
    'Traversable',
    'RunserverCommand',
    'RunIndexCommand',
    'RunAppCommand',
]


@dataclass
class BaseCommand:
    """Base class for all commands."""


class DummyMixin:
    """Simple mixin that add empty or default values."""
    now: str = ''
    revision: str = ''
    branch: str = 'all'
    leaf: str = 'all'
    force: bool = False
    dry_run: bool = False


@dataclass
class FilesRelatedCommand(BaseCommand, DummyMixin):
    """Works mainly with files."""
    root_folder: str = ''
    sources_folder: str = ''
    storage_folder: str = ''
    content_folder: str = ''
    database_folder: str = ''


@dataclass
class UniteCommand(FilesRelatedCommand):
    """We have nothing ready, lets create base unit of source information."""
    name: str = 'unite'


@dataclass
class MakeRelocationsCommand(FilesRelatedCommand):
    """We have parsed source file, lets create some relocation files."""
    name: str = 'make_relocations'


@dataclass
class MakeMigrationsCommand(FilesRelatedCommand):
    """We have parsed source file, lets create some migration files."""
    name: str = 'make_migrations'


@dataclass
class MigrateCommand(FilesRelatedCommand):
    """We have migrations, lets apply them to leaf databases."""
    name: str = 'migrate'


@dataclass
class RelocateCommand(FilesRelatedCommand):
    """Move and compress actual media content."""
    name: str = 'relocate'


@dataclass
class SyncCommand(FilesRelatedCommand):
    """We have filled leaf databases, lets gather information into root."""
    name: str = 'sync'


@dataclass
class FreezeCommand(FilesRelatedCommand):
    """Create static database."""
    name: str = 'freeze'


@dataclass
class ShowTreeCommand(BaseCommand, DummyMixin):
    """Display folder tree."""
    root_folder: str = ''
    sources_folder: str = ''
    name: str = 'show_tree'


@dataclass
class RSyncCommand(BaseCommand, DummyMixin):
    """Synchronize two content folders."""
    root_folder: str = ''
    root_folder_to: str = ''
    content_folder: str = ''
    content_folder_to: str = ''
    name: str = 'rsync'


# Command that can be used in walking
Traversable = FilesRelatedCommand | ShowTreeCommand | RSyncCommand


@dataclass
class RunserverCommand(BaseCommand):
    """Start web application."""
    host: str = ''
    port: int = 0
    reload: bool = False
    static: bool = False
    root_folder: str = ''
    content_folder: str = '.'
    database_folder: str = '.'
    templates_folder: str = '.'
    static_folder: str = '.'
    injection: str = ''
    name: str = 'runserver'


@dataclass
class RunIndexCommand(BaseCommand):
    """Start index server."""
    host: str = ''
    port: int = 0
    root_folder: str = ''
    database_folder: str = '.'
    name: str = 'run_index'


@dataclass
class RunAppCommand(BaseCommand):
    """Start web application."""
    host: str = ''
    port: int = 0
    reload: bool = False
    debug: bool = False
    static: bool = False
    root_folder: str = ''
    content_folder: str = ''
    database_folder: str = ''
    templates_folder: str = ''
    static_folder: str = ''
    name: str = 'run_app'
