# -*- coding: utf-8 -*-

"""Main control tool.

Possible call variants:

    To analyze source files and create unit files:
        python -m omoide unite --branch=all --leaf=all

    To make migrations:
        python -m omoide make_migrations --branch=all --leaf=all

    To make relocations:
        python -m omoide make_relocations --branch=all --leaf=all

    To perform migrations:
        python -m omoide migrate --branch=all --leaf=all

    To relocate and resize media files:
        python -m omoide relocate --branch=all --leaf=all

    To synchronize databases:
        python -m omoide sync --branch=all --leaf=all

    To create final static app_database:
        python -m omoide freeze

    To launch development server:
        python -m omoide runserver
        python -m omoide runserver --host=127.0.0.1 --port9000

    To display folder structure:
        python -m omoide show_tree
"""
import sys
from typing import Callable

import click

from omoide import commands, infra
from omoide import constants
from omoide.commands import perform
from omoide.migration_engine.operations.unite import persistent


def run(command: commands.BaseCommand,
        filesystem: infra.Filesystem = infra.Filesystem(),
        stdout: infra.STDOut = infra.STDOut()) -> None:
    """Start of execution."""
    _abs = filesystem.absolute

    if isinstance(command, commands.FilesRelatedCommand):
        command.sources_folder = _abs(command.sources_folder)
        command.storage_folder = _abs(command.storage_folder)
        command.content_folder = _abs(command.content_folder)
        command.database_folder = _abs(command.database_folder)
        filesystem.ensure_folder_exists(command.storage_folder, stdout)
        filesystem.ensure_folder_exists(command.content_folder, stdout)
        assert_sources_folder_exist(command, filesystem, stdout)

        if command.now:
            persistent.set_now(command.now)

        if command.revision:
            persistent.set_revision(command.revision)

    elif isinstance(command, commands.RunserverCommand):
        command.content_folder = _abs(command.content_folder)
        command.database_folder = _abs(command.database_folder)
        command.templates_folder = _abs(command.templates_folder)
        command.static_folder = _abs(command.static_folder)

    target_func = get_target_func(command)
    target_func(command, filesystem, stdout)


def assert_sources_folder_exist(command: commands.FilesRelatedCommand,
                                filesystem: infra.Filesystem,
                                stdout: infra.STDOut) -> None:
    """Stop execution if source folder does not exist."""
    if filesystem.not_exists(command.sources_folder):
        stdout.red(f'Sources folder does not exist: {command.sources_folder}')
        sys.exit(1)


def get_target_func(command: commands.BaseCommand) -> Callable:
    """Return perform func based on domain."""
    target_func = {
        'unite': perform.perform_unite,
        'make_migrations': perform.perform_make_migrations,
        'make_relocations': perform.perform_make_relocations,
        'migrate': perform.perform_migrate,
        'relocate': perform.perform_relocate,
        'sync': perform.perform_sync,
        'freeze': perform.perform_freeze,
        'show_tree': perform.perform_show_tree,
        'runserver': perform.perform_runserver,
    }[getattr(command, 'name')]

    return target_func


@click.group()
def cli():
    """Store media materials, search by tags, browse content."""


@cli.command(name='runserver',
             help='Run development web server ')
@click.option('--host',
              default=constants.DEFAULT_SERVER_HOST,
              help='Host to run web server on')
@click.option('--port',
              default=constants.DEFAULT_SERVER_PORT,
              help='Port to run web server on')
@click.option('--reload/--no-reload',
              default=False,
              help='Realtime reload for application code')
@click.option('--static/--no-static',
              default=False,
              help='Serve static from web app (use only for development)')
@click.option('--content-folder',
              default=constants.DEFAULT_CONTENT_FOLDER,
              help='Where to load media content from (only if static is on)')
@click.option('--database-folder',
              default=constants.DEFAULT_DATABASE_FOLDER,
              help='Where to load database from')
@click.option('--templates-folder',
              default=constants.DEFAULT_TEMPLATES_FOLDER,
              help='Where to load templates from')
@click.option('--static-folder',
              default=constants.DEFAULT_STATIC_FOLDER,
              help='Where to load static from (only if static is on)')
def cmd_runserver(**kwargs) -> None:
    """Command that starts web server."""
    command = commands.RunserverCommand(**kwargs)
    run(command)


def _function_factory(name: str, _command_type: type) -> Callable:
    """Create function with given name."""

    def _new_func(**kwargs) -> None:
        """Actual execution starter.

        We need so many wrappers because all those decorators
        could not be applied in a simple cycle. Last applied
        instance will just overwrite all.
        """
        command = _command_type(**kwargs)
        run(command)

    _new_func.__name__ = name
    return _new_func


_FILE_RELATED_COMMANDS = [
    ('unite',
     'Make initial instructions from source files',
     commands.UniteCommand),
    ('make_relocations',
     'Create list of files to convert',
     commands.MakeRelocationsCommand),
    ('make_migrations',
     'Create list of SQL command to apply',
     commands.MakeMigrationsCommand),
    ('migrate',
     'Apply previously generated SQL commands',
     commands.MigrateCommand),
    ('relocate',
     'Apply previously generated relocation commands',
     commands.RelocateCommand),
    ('sync',
     'Synchronize leaf databases and form root db',
     commands.SyncCommand),
    ('freeze',
     'Construct production ready db from local ones',
     commands.FreezeCommand),
    ('show_tree',
     'Display folder structure of source folder',
     commands.ShowTreeCommand),
]

_FILE_RELATED_DECORATORS = [
    click.option('--branch',
                 default='all',
                 help='branch to work on (folder name)'),
    click.option('--leaf',
                 default='all',
                 help='leaf to work on (folder name)'),
    click.option('--force/--no-force',
                 default=False,
                 help='Overwrite existing files'),
    click.option('--dry-run/--no-dry-run',
                 default=False,
                 help='Only display info without performing operation'),
    click.option('--sources-folder',
                 default=constants.DEFAULT_SOURCES_FOLDER,
                 help='Where to look for source files'),
    click.option('--storage-folder',
                 default=constants.DEFAULT_STORAGE_FOLDER,
                 help='Where to save intermediate results'),
    click.option('--content-folder',
                 default=constants.DEFAULT_CONTENT_FOLDER,
                 help='Where to save media content'),
    click.option('--database-folder',
                 default=constants.DEFAULT_DATABASE_FOLDER,
                 help='Where to save created database'),
    click.option('--now',
                 default='',
                 help='Which time should be embedded into migration'),
    click.option('--revision',
                 default='',
                 help='Which revision should be embedded into migration'),
]


for command_name, help_text, command_type in _FILE_RELATED_COMMANDS:
    # noinspection PyRedeclaration
    func = _function_factory(command_name, command_type)
    func = cli.command(name=command_name, help=help_text)(func)

    for decorator in _FILE_RELATED_DECORATORS:
        func = decorator(func)

if __name__ == '__main__':
    cli()
