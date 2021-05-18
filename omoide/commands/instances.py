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
    'RunserverCommand',
]


@dataclass
class BaseCommand:
    """Base class for all commands."""


@dataclass
class FilesRelatedCommand(BaseCommand):
    """Works mainly with files."""
    now: str = ''
    revision: str = ''
    sources_folder: str = ''
    storage_folder: str = ''
    content_folder: str = ''
    database_folder: str = ''
    branch: str = 'all'
    leaf: str = 'all'
    force: bool = False
    dry_run: bool = False


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
    """Create static app_database."""
    name: str = 'freeze'


@dataclass
class ShowTreeCommand(FilesRelatedCommand):
    """Display folder tree."""
    name: str = 'show_tree'


@dataclass
class RunserverCommand(BaseCommand):
    """Start web application."""
    host: str = ''
    port: int = 0
    reload: bool = False
    static: bool = False
    content_folder: str = '.'
    database_folder: str = '.'
    templates_folder: str = '.'
    static_folder: str = '.'
    injection: str = ''
    name: str = 'runserver'
