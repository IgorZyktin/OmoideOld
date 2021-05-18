# -*- coding: utf-8 -*-

"""Make relocations.
"""
from typing import List

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.migration_engine import entities, classes


# pylint: disable=too-many-locals
def act(command: commands.MakeRelocationsCommand,
        filesystem: infra.Filesystem,
        stdout: infra.STDOut) -> int:
    """Make relocations."""
    walk = infra.walk_sources_from_command(command, filesystem)

    total_new_relocations = 0
    for branch, leaf, _ in walk:
        storage_folder = filesystem.join(command.storage_folder, branch, leaf)
        unit_file_path = filesystem.join(storage_folder,
                                         constants.UNIT_FILE_NAME)

        if filesystem.not_exists(unit_file_path):
            stdout.gray(f'\t[{branch}][{leaf}] Unit file does not exist')
            continue

        relocation_file_path = filesystem.join(storage_folder,
                                               constants.RELOCATION_FILE_NAME)

        if filesystem.exists(relocation_file_path) and not command.force:
            stdout.cyan(f'\t[{branch}][{leaf}] Relocation file already exist')
            continue

        relocations: List[classes.Relocation] = []
        unit_dict = filesystem.read_json(unit_file_path)
        unit = entities.Unit(**unit_dict)

        for meta in unit.metas:
            new_relocations = make_relocations_for_one_meta(
                command=command,
                meta=meta,
                branch=branch,
                leaf=leaf,
                filesystem=filesystem,
            )
            relocations.append(new_relocations)
            total_new_relocations += 1

        save_relocations(
            folder=storage_folder,
            relocations=relocations,
            filesystem=filesystem,
        )
        stdout.green(f'\t[{branch}][{leaf}] Created relocations')

    return total_new_relocations


def make_relocations_for_one_meta(command: commands.MakeRelocationsCommand,
                                  meta: entities.Meta,
                                  branch: str,
                                  leaf: str,
                                  filesystem: infra.Filesystem
                                  ) -> classes.Relocation:
    """Gather all required resources for relocation information."""
    _, _, theme, group, _ = meta.path_to_content.split('/')

    operations = [
        classes.Operation(
            width=meta.width,
            height=meta.height,
            folder_to=filesystem.join(command.content_folder,
                                      constants.MEDIA_CONTENT_FOLDER_NAME,
                                      theme, group),
            operation_type='copy',
        ),
        classes.Operation(
            width=constants.PREVIEW_SIZE[0],
            height=constants.PREVIEW_SIZE[1],
            folder_to=filesystem.join(command.content_folder,
                                      constants.MEDIA_PREVIEW_FOLDER_NAME,
                                      theme, group),
            operation_type='scale',
        ),
        classes.Operation(
            width=constants.THUMBNAIL_SIZE[0],
            height=constants.THUMBNAIL_SIZE[1],
            folder_to=filesystem.join(command.content_folder,
                                      constants.MEDIA_THUMBNAILS_FOLDER_NAME,
                                      theme, group),
            operation_type='scale',
        ),
    ]

    relocation = classes.Relocation(
        uuid=meta.uuid,
        source_filename=f'{meta.original_filename}.{meta.original_extension}',
        target_filename=f'{meta.uuid}.{meta.original_extension}',
        folder_from=filesystem.join(command.sources_folder, branch, leaf,
                                    theme, group),
        operations=operations,
    )

    return relocation


def save_relocations(folder: str,
                     relocations: List[classes.Relocation],
                     filesystem: infra.Filesystem) -> str:
    """Save relocations as JSON file."""
    file_path = filesystem.join(folder, constants.RELOCATION_FILE_NAME)
    filesystem.write_json(file_path, [x.dict() for x in relocations])
    return file_path
