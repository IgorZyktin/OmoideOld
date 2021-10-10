# -*- coding: utf-8 -*-

"""Main control tool.

Possible call variants:

    To launch example:
        python -m omoide example

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

    To create final static database:
        python -m omoide freeze

    To launch development server:
        python -m omoide runserver
        python -m omoide runserver --host=127.0.0.1 --port9000

    To launch index server:
        python -m omoide run_index

    To display folder structure:
        python -m omoide show_tree
"""
import sys
from typing import Callable

import click

from omoide import commands, infra
from omoide import constants
from omoide.commands import perform
from omoide.index_server import constants as index_constants


def run_using_files(command: commands.FilesRelatedCommand,
                    filesystem: infra.Filesystem = infra.Filesystem(),
                    stdout: infra.STDOut = infra.STDOut()) -> None:
    """Start of execution."""
    from omoide.migration_engine.operations.unite import persistent
    _abs = filesystem.absolute
    _join = filesystem.join

    command.sources_folder = _abs(_join(command.root_folder,
                                        constants.SOURCES_FOLDER_NAME))
    command.storage_folder = _abs(_join(command.root_folder,
                                        constants.STORAGE_FOLDER_NAME))
    command.content_folder = _abs(_join(command.root_folder,
                                        constants.CONTENT_FOLDER_NAME))
    command.database_folder = _abs(_join(command.root_folder,
                                         constants.DATABASE_FOLDER_NAME))

    assert_sources_folder_exist(command, filesystem, stdout)
    filesystem.ensure_folder_exists(command.storage_folder, stdout)
    filesystem.ensure_folder_exists(command.content_folder, stdout)

    if command.now:
        persistent.set_now(command.now)

    if command.revision:
        persistent.set_revision(command.revision)

    target_func = get_target_func(command)
    target_func(command, filesystem, stdout)


def run_using_server(command: commands.RunserverCommand,
                     filesystem: infra.Filesystem = infra.Filesystem(),
                     stdout: infra.STDOut = infra.STDOut()) -> None:
    """Start of execution."""
    _abs = filesystem.absolute
    _join = filesystem.join
    cwd = filesystem.absolute('.')
    command.content_folder = _abs(_join(command.root_folder,
                                        constants.CONTENT_FOLDER_NAME))
    command.database_folder = _abs(_join(command.root_folder,
                                         constants.DATABASE_FOLDER_NAME))

    command.templates_folder = _abs(_join(cwd,
                                          *constants.DEFAULT_TEMPLATES_PATH))
    command.static_folder = _abs(_join(cwd,
                                       *constants.DEFAULT_STATIC_PATH))

    perform.perform_runserver(command, filesystem, stdout)


def _apply_source_paths(command, filesystem: infra.Filesystem) -> None:
    """Alter command inplace and fill sources related paths."""
    root = command.root.strip('"').strip("'") or '.'
    root = filesystem.absolute(root)

    if hasattr(command, 'content_folder'):
        command.content_folder = filesystem.absolute(
            filesystem.join(root, constants.CONTENT_FOLDER_NAME)
        )

    if hasattr(command, 'database_folder'):
        command.database_folder = filesystem.absolute(
            filesystem.join(root, constants.DATABASE_FOLDER_NAME)
        )


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
    }[getattr(command, 'name')]

    return target_func


@click.group()
def cli():
    """Store media materials, search by tags, browse content."""


@cli.command(name='run_index',
             help='Run search machine index server')
@click.option('--host',
              default=index_constants.HOST,
              help='Host to run index server on')
@click.option('--port',
              default=index_constants.PORT,
              help='Port to run index server on')
@click.option('--root',
              default=constants.DEFAULT_ROOT_FOLDER,
              help='Path to the main data containing folder')
def cmd_run_index(**kwargs) -> None:
    """Command that starts web server."""
    command = commands.RunIndexCommand(**kwargs)
    filesystem = infra.Filesystem()
    stdout = infra.STDOut()
    _apply_source_paths(command, filesystem)

    perform.perform_run_index(command, filesystem, stdout)


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
@click.option('--root-folder',
              default=constants.DEFAULT_ROOT_FOLDER,
              help='Where to load content from')
def cmd_runserver(**kwargs) -> None:
    """Command that starts web server."""
    command = commands.RunserverCommand(**kwargs)
    run_using_server(command)


@cli.command(name='example',
             help='Run example app')
def cmd_example() -> None:
    """Command that starts demo server."""
    import os
    cwd = os.path.abspath(os.getcwd())
    root = os.path.join(cwd, 'omoide', 'example')

    command = commands.RunserverCommand(
        host=constants.DEFAULT_SERVER_HOST,
        port=constants.DEFAULT_SERVER_PORT,
        reload=True,
        static=True,
        root_folder=root,
        content_folder=os.path.join(root, 'example',
                                    constants.CONTENT_FOLDER_NAME),
        database_folder=os.path.join(root, 'example',
                                     constants.DATABASE_FOLDER_NAME),
        templates_folder=os.path.join(cwd, *constants.
                                      DEFAULT_TEMPLATES_PATH),
        static_folder=os.path.join(cwd, *constants.DEFAULT_STATIC_PATH),
    )
    run_using_server(command)


def _function_factory(name: str, _command_type: type) -> Callable:
    """Create function with given name."""

    def _new_func(**kwargs) -> None:
        """Actual execution starter.

        We need so many wrappers because all those decorators
        could not be applied in a simple cycle. Last applied
        instance will just overwrite all.
        """
        command = _command_type(**kwargs)
        run_using_files(command)

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
    click.option('--root-folder',
                 default=constants.DEFAULT_ROOT_FOLDER,
                 help='Where to load content from'),
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
