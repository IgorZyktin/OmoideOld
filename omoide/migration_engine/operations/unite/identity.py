# -*- coding: utf-8 -*-

"""Tools required to generate unique identifiers.
"""
from itertools import chain

from omoide import constants, infra
from omoide.migration_engine.operations.unite.class_identity_master import (
    IdentityMaster
)
from omoide.migration_engine.operations.unite.class_router import Router
from omoide.migration_engine.operations.unite.class_uuid_master import (
    UUIDMaster
)


def gather_existing_identities(storage_folder: str,
                               router: Router,
                               identity_master: IdentityMaster,
                               uuid_master: UUIDMaster,
                               filesystem: infra.Filesystem) -> None:
    """Get all variables and all UUID from existing files."""
    for branch, leaf, leaf_folder in infra.walk(storage_folder, filesystem):

        unit_path = filesystem.join(leaf_folder, constants.UNIT_FILE_NAME)
        if filesystem.exists(unit_path):
            unit = filesystem.read_json(unit_path)
            gather_routes_from_unit(unit, router)

        cache_path = filesystem.join(leaf_folder, constants.CACHE_FILE_NAME)
        if filesystem.exists(cache_path):
            cache = filesystem.read_json(cache_path)
            gather_variables_from_cache(branch, leaf, cache,
                                        identity_master, uuid_master)


def gather_routes_from_unit(raw_unit: dict, router: Router) -> None:
    """Find all routes in given unit and store them into router."""
    objects = chain(raw_unit.get('themes', []), raw_unit.get('groups', []))

    for each in objects:
        router.register_route(each['uuid'], each['route'])


def gather_variables_from_cache(branch: str, leaf: str, cache: dict,
                                identity_master: IdentityMaster,
                                uuid_master: UUIDMaster) -> None:
    """Find all variables in given cache and store them in Identity master."""
    uuid_type_by_category = {'themes': constants.PREFIX_THEME,
                             'groups': constants.PREFIX_GROUP,
                             'metas': constants.PREFIX_META,
                             'synonyms': constants.PREFIX_SYNONYM}

    for category, variables in cache.get('variables', {}).items():
        uuid_type = uuid_type_by_category[category]
        for name, value in variables.items():
            identity_master.add_variable(branch, leaf, uuid_type, name, value)
            uuid_master.add_existing_uuid(value)
