# -*- coding: utf-8 -*-

"""Make relocations.
"""
from dataclasses import asdict
from typing import List

from omoide import commands
from omoide import infra
from omoide.constants import media as media_const
from omoide.constants import storage as storage_const
from omoide.migration_engine import entities, classes


# pylint: disable=too-many-locals
def act(command: commands.MakeRelocationsCommand,
        filesystem: infra.Filesystem,
        stdout: infra.STDOut) -> int:
    """Make relocations."""
    renderer = classes.Renderer()
    walk = infra.walk_sources_from_command(command, filesystem)

    total_new_relocations = 0
    for branch, leaf, _ in walk:
        storage_folder = filesystem.join(command.storage_folder, branch, leaf)
        unit_file_path = filesystem.join(storage_folder,
                                         storage_const.UNIT_FILE_NAME)

        if filesystem.not_exists(unit_file_path):
            stdout.gray(f'\t[{branch}][{leaf}] Unit file does not exist')
            continue

        relocation_file_path = filesystem.join(
            storage_folder, storage_const.RELOCATION_FILE_NAME)

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
                renderer=renderer,
            )
            relocations.extend(new_relocations)
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
                                  filesystem: infra.Filesystem,
                                  renderer: classes.Renderer,
                                  ) -> List[classes.Relocation]:
    """Gather all required resources for relocation information."""
    _, _, theme, group, _ = meta.path_to_content.split('/')
    source_filename = f'{meta.original_filename}.{meta.original_extension}'

    def get_last_segment(path: str) -> str:
        """Extract filename."""
        head, ext = path.rsplit('.', maxsplit=1)
        filename = head[-38:]
        return f'{filename}.{ext}'

    preview_width, preview_height = renderer.calculate_size(
        meta.width, meta.height,
        media_const.PREVIEW_WIDTH, media_const.PREVIEW_HEIGHT)

    thumbnail_width, thumbnail_height = renderer.calculate_size(
        meta.width, meta.height,
        media_const.THUMBNAIL_WIDTH, media_const.THUMBNAIL_HEIGHT)

    relocations = [
        classes.Relocation(
            uuid=meta.uuid,
            width=meta.width,
            height=meta.height,
            folder_from=filesystem.join(
                command.sources_folder, branch, leaf, theme, group),
            folder_to=filesystem.join(
                command.content_folder,
                storage_const.MEDIA_CONTENT_FOLDER_NAME, theme, group),
            operation_type='copy',
            source_filename=source_filename,
            target_filename=get_last_segment(meta.path_to_content),
        ),
        classes.Relocation(
            uuid=meta.uuid,
            width=preview_width,
            height=preview_height,
            folder_from=filesystem.join(
                command.sources_folder, branch, leaf, theme, group),
            folder_to=filesystem.join(
                command.content_folder,
                storage_const.MEDIA_PREVIEW_FOLDER_NAME, theme, group),
            operation_type='scale',
            source_filename=source_filename,
            target_filename=get_last_segment(meta.path_to_preview),
        ),
        classes.Relocation(
            uuid=meta.uuid,
            width=thumbnail_width,
            height=thumbnail_height,
            folder_from=filesystem.join(
                command.sources_folder, branch, leaf, theme, group),
            folder_to=filesystem.join(
                command.content_folder,
                storage_const.MEDIA_THUMBNAILS_FOLDER_NAME, theme, group),
            operation_type='scale',
            source_filename=source_filename,
            target_filename=get_last_segment(meta.path_to_thumbnail),
        ),
    ]

    return relocations


def save_relocations(folder: str,
                     relocations: List[classes.Relocation],
                     filesystem: infra.Filesystem) -> str:
    """Save relocations as JSON file."""
    file_path = filesystem.join(folder, storage_const.RELOCATION_FILE_NAME)
    filesystem.write_json(file_path, [asdict(x) for x in relocations])
    return file_path
