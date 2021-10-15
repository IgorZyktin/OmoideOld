# -*- coding: utf-8 -*-

"""Process source files.
"""
import json
import sys
from typing import Optional, NoReturn, Dict

import pydantic

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.infra import walking
from omoide.migration_engine import classes
from omoide.migration_engine import entities
from omoide.migration_engine.classes import passport as passport_module
from omoide.migration_engine.operations.unite import identity
from omoide.migration_engine.operations.unite import preprocessing
from omoide.migration_engine.operations.unite import raw_entities
from omoide.migration_engine.operations.unite.class_identity_master import (
    IdentityMaster
)
from omoide.migration_engine.operations.unite.class_router import Router
from omoide.migration_engine.operations.unite.class_uuid_master import (
    UUIDMaster
)


def act(command: commands.UniteCommand,
        filesystem: infra.Filesystem,
        stdout: infra.STDOut) -> int:
    """Process source files.
    """
    router = Router()
    identity_master = IdentityMaster()
    uuid_master = UUIDMaster()
    renderer = classes.Renderer()

    identity.gather_existing_identities(
        storage_folder=command.storage_folder,
        router=router,
        identity_master=identity_master,
        uuid_master=uuid_master,
        filesystem=filesystem,
    )

    total_new_units = 0
    for top in walking.traverse_top(command, filesystem, 'sources_folder'):
        stdout.print(f'\t{top}')

        for bottom in walking.traverse_bottom(command, top):
            source_path = filesystem.join(bottom.leaf_folder,
                                          constants.SOURCE_FILE_NAME)
            if filesystem.not_exists(source_path):
                stdout.gray(f'\t\t{bottom} Source file does not exist')
                continue

            passport = passport_module.load_from_file(bottom)

            if passport.already_processed(bottom, source_path,
                                          passport.unite.fingerprints) \
                    and not command.force:
                stdout.cyan(f'\t\t{bottom} Unit file already processed')
                continue

            new_path = make_unit_in_leaf(
                command=command,
                bottom=bottom,
                router=router,
                identity_master=identity_master,
                uuid_master=uuid_master,
                renderer=renderer,
                stdout=stdout,
            )

            passport.register_unite(bottom, source_path)
            passport.save_to_file(bottom)

            if new_path:
                stdout.green(f'\t\t{bottom} Created unit file')
                total_new_units += 1

    return total_new_units


# pylint: disable=too-many-locals
def make_unit_in_leaf(command: commands.UniteCommand,
                      bottom: walking.Bottom,
                      router: Router,
                      identity_master: IdentityMaster,
                      uuid_master: UUIDMaster,
                      renderer: classes.Renderer,
                      stdout: infra.STDOut) -> Optional[str]:
    """Create single unit file."""
    uuids = load_cached_uuids(bottom, command.storage_folder)
    identity_master.add_files_cache(uuids)

    unit = make_unit(bottom=bottom,
                     router=router,
                     identity_master=identity_master,
                     uuid_master=uuid_master,
                     renderer=renderer,
                     stdout=stdout)

    cache = {
        'variables': identity_master.extract_variables(bottom),
        'uuids': identity_master.extract_files_cache(),
    }

    unit_folder = bottom.filesystem.join(command.storage_folder,
                                         bottom.branch, bottom.leaf)
    unit_path = bottom.filesystem.join(unit_folder, constants.UNIT_FILE_NAME)

    if not command.dry_run:
        bottom.filesystem.ensure_folder_exists(unit_folder, stdout)

        unit_dict = unit.dict()
        unit_text = json.dumps(unit_dict)
        assert_no_variables(unit_text, stdout)
        bottom.filesystem.write_json(unit_path, unit_dict)

        cache_path = bottom.filesystem.join(unit_folder,
                                            constants.CACHE_FILE_NAME)
        bottom.filesystem.write_json(cache_path, cache)
        return unit_path

    return None


def make_unit(bottom: walking.Bottom,
              router: Router,
              identity_master: IdentityMaster,
              uuid_master: UUIDMaster,
              renderer: classes.Renderer,
              stdout: infra.STDOut) -> entities.Unit:
    """Combine all updates in big JSON file."""
    source_path = bottom.filesystem.join(bottom.leaf_folder,
                                         constants.SOURCE_FILE_NAME)
    source_raw_text = bottom.filesystem.read_file(source_path)
    source_text = preprocessing.preprocess_source(
        text=source_raw_text,
        branch=bottom.branch,
        leaf=bottom.leaf,
        identity_master=identity_master,
        uuid_master=uuid_master,
    )
    source_dict = json.loads(source_text)
    source = instantiate_source(source_dict, stdout)

    unit = entities.Unit()
    preprocessing.do_themes(source, unit, router)
    preprocessing.do_groups(source, bottom, unit, router, identity_master,
                            uuid_master, renderer)
    preprocessing.do_synonyms(source, unit)
    preprocessing.do_no_group_metas(source, bottom, unit, router,
                                    identity_master, uuid_master, renderer)

    return unit


def instantiate_source(raw_source: dict,
                       stdout: infra.STDOut) -> raw_entities.Source:
    """Safely create Source or display contents on exception."""
    targets = [
        ('themes', raw_entities.Theme),
        ('groups', raw_entities.Group),
        ('metas', raw_entities.Meta),
        ('synonyms', raw_entities.Synonym),
    ]

    payload = {}

    for target_category, target_type in targets:
        content = raw_source.get(target_category, [])
        elements = []

        for each in content:
            try:
                element = target_type(**each)
            except pydantic.error_wrappers.ValidationError:
                stdout.red(
                    'Failed on:\n' + json.dumps(each, indent=4,
                                                ensure_ascii=False)
                )
                raise
            else:
                elements.append(element)

        payload[target_category] = elements

    return raw_entities.Source(**payload)


def assert_no_variables(unit_text: str,
                        stdout: infra.STDOut) -> Optional[NoReturn]:
    """Raise if variables are still present in output."""
    index = unit_text.find(constants.VARIABLE_SIGN)
    if index != -1:
        left = max(index - constants.VARIABLE_SEARCH_WINDOW, 0)
        right = index + constants.VARIABLE_SEARCH_WINDOW
        fragment = unit_text[left:right]
        stdout.red(
            'Seems like output unit still contains some variables:'
            f'\n...{fragment}...\n'
        )
        sys.exit(1)
    return None


def load_cached_uuids(bottom: walking.Bottom,
                      storage_folder: str) -> Dict[str, Dict[str, str]]:
    """Load uuids cache for current target."""
    path = bottom.filesystem.join(
        storage_folder,
        bottom.branch,
        bottom.leaf,
        constants.CACHE_FILE_NAME,
    )

    if bottom.filesystem.exists(path):
        uuids = bottom.filesystem.read_json(path).get('uuids', {})
    else:
        uuids = {}

    return uuids
