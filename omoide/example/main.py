# -*- coding: utf-8 -*-

"""Prepare resources and launch application.
"""
from contextlib import suppress

from omoide import infra, constants
from omoide.__main__ import cli as omoide_
from omoide.migration_engine.operations.unite import persistent


def main():
    """Entry point.
    """
    # added to avoid constant updates in example with each release
    # not really supposed to be used in actual work
    persistent.set_now('2021-08-20 00:00:00')
    persistent.set_revision('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

    # with suppress(SystemExit):
    #     omoide_(['unite'])

    # with suppress(SystemExit):
    #     omoide_(['make_migrations'])

    # with suppress(SystemExit):
    #     omoide_(['make_relocations'])

    # with suppress(SystemExit):
    #     omoide_(['migrate'])

    # with suppress(SystemExit):
    #     omoide_(['relocate'])

    # with suppress(SystemExit):
    #     omoide_(['sync'])

    with suppress(SystemExit):
        omoide_(['freeze'])

    # with suppress(SystemExit):
    #     filesystem = infra.Filesystem()
    #     root = filesystem.absolute('..')
    #     app_folder = filesystem.join(root, 'omoide', 'application')
    #     templates_folder = filesystem.join(app_folder,
    #                                        constants.TEMPLATES_FOLDER_NAME)
    #     static_folder = filesystem.join(app_folder,
    #                                     constants.STATIC_FOLDER_NAME)
    #     database_folder = filesystem.join(filesystem.absolute('.'),
    #                                       constants.DATABASE_FOLDER_NAME)
    #     omoide_(['runserver',
    #              f'--static',
    #              f'--app_database-folder={database_folder}',
    #              f'--templates-folder={templates_folder}',
    #              f'--static-folder={static_folder}'])


if __name__ == '__main__':
    main()
