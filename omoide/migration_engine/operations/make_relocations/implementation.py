# -*- coding: utf-8 -*-

"""Make relocations.
"""
from omoide import commands
from omoide import infra
from omoide.infra import walking
from omoide.constants import media as media_const
from omoide.constants import storage as storage_const
from omoide.migration_engine import entities, classes
from omoide import constants
from omoide.migration_engine.classes import passport as passport_module


# pylint: disable=too-many-locals
def run_make_relocations(command: commands.MakeRelocationsCommand,
                         filesystem: infra.Filesystem,
                         stdout: infra.STDOut) -> int:
    """Make relocations."""
    renderer = classes.Renderer()

    total_new_relocations = 0
    for top in walking.traverse_top(command, filesystem):
        stdout.print(f'\t{top}')

        for bottom in walking.traverse_bottom(command, top):
            unit_file_path = filesystem.join(
                bottom.leaf_folder,
                constants.UNIT_FILE_NAME,
            )

            if filesystem.not_exists(unit_file_path):
                stdout.gray(f'\t\t{bottom} Unit file does not exist')
                continue

            passport = passport_module.load_from_file(bottom)

            if passport.already_processed(
                    bottom, unit_file_path,
                    passport.make_relocations.fingerprints) \
                    and not command.force:
                stdout.cyan(f'\t\t[{bottom} Relocations already created')
                continue

            unit_dict = filesystem.read_json(unit_file_path)
            unit = entities.Unit(**unit_dict)
            relocation = classes.Relocation()

            for meta in unit.metas:
                _, _, theme, group, _ = meta.path_to_content.split('/')
                key = f'{theme},{group}'

                if key in relocation.groups:
                    relocation_group = relocation.groups[key]
                else:
                    relocation_group = classes.OneGroup(
                        folder_from=filesystem.join(
                            command.sources_folder,
                            bottom.branch,
                            bottom.leaf,
                            theme,
                            group),
                    )
                    relocation.groups[key] = relocation_group

                new_file = make_relocations_for_one_meta(
                    command=command,
                    meta=meta,
                    theme=theme,
                    group=group,
                    filesystem=filesystem,
                    renderer=renderer,
                )
                relocation_group.files[meta.uuid] = new_file
                total_new_relocations += len(new_file.conversions)

            save_relocation(
                folder=filesystem.join(command.storage_folder,
                                       bottom.branch,
                                       bottom.leaf),
                relocation=relocation,
                filesystem=filesystem,
            )
            stdout.green(f'\t\t{bottom} Created relocations')
            passport.register_make_relocations(bottom, unit_file_path)
            passport.save_to_file(bottom)

    return total_new_relocations


def make_relocations_for_one_meta(command: commands.MakeRelocationsCommand,
                                  meta: entities.Meta,
                                  theme: str,
                                  group: str,
                                  filesystem: infra.Filesystem,
                                  renderer: classes.Renderer,
                                  ) -> classes.OneFile:
    """Gather all required resources for relocation information."""
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

    return classes.OneFile(
        uuid=meta.uuid,
        source_filename=source_filename,
        target_filename=get_last_segment(meta.path_to_content),
        conversions=[
            classes.OneConversion(
                width=meta.width,
                height=meta.height,
                folder_to=filesystem.join(
                    command.content_folder,
                    storage_const.MEDIA_CONTENT_FOLDER_NAME, theme, group),
                operation_type='copy',
            ),
            classes.OneConversion(
                width=preview_width,
                height=preview_height,
                folder_to=filesystem.join(
                    command.content_folder,
                    storage_const.MEDIA_PREVIEW_FOLDER_NAME, theme, group),
                operation_type='scale',

            ),
            classes.OneConversion(
                width=thumbnail_width,
                height=thumbnail_height,
                folder_to=filesystem.join(
                    command.content_folder,
                    storage_const.MEDIA_THUMBNAILS_FOLDER_NAME, theme, group),
                operation_type='scale',
            )
        ]
    )


def save_relocation(folder: str,
                    relocation: classes.Relocation,
                    filesystem: infra.Filesystem) -> str:
    """Save relocations as JSON file."""
    file_path = filesystem.join(folder, storage_const.RELOCATION_FILE_NAME)
    filesystem.write_json(file_path, relocation.dict())
    return file_path
