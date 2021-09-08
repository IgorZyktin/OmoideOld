# -*- coding: utf-8 -*-

"""Textual preprocessing components.
"""
import operator
import re
from typing import Union, List, Type, Tuple, Dict, Callable, Optional

from omoide import constants
from omoide import infra
from omoide.migration_engine import classes, entities
from omoide.migration_engine.operations.unite import persistent, raw_entities
from omoide.migration_engine.operations.unite \
    .class_identity_master import IdentityMaster
from omoide.migration_engine.operations.unite \
    .class_router import Router
from omoide.migration_engine.operations.unite \
    .class_uuid_master import UUIDMaster

CastTypes = Union[
    entities.TagTheme,
    entities.TagGroup,
    entities.TagMeta,
    entities.SynonymValue,
]


def preprocess_source(text: str, branch: str, leaf: str,
                      identity_master: IdentityMaster,
                      uuid_master: UUIDMaster) -> str:
    """Convert template of the sources file into renderable one.

    Here we're substituting variables and extending contents.
    """
    text = generate_variables(text, branch, leaf, identity_master, uuid_master)
    text = apply_variables(text, identity_master)
    return text


def generate_variables(text: str, branch: str, leaf: str,
                       identity_master: IdentityMaster,
                       uuid_master: UUIDMaster) -> str:
    """Substitute UUID variables in the source text."""
    pattern = re.compile(constants.UUID_MAKE_VARIABLE_PATTERN, re.IGNORECASE)

    _to_replace: List[Tuple[str, str]] = []

    for match in re.finditer(pattern, text):
        uuid_type, variable_name = match.groups()
        variable_value = identity_master.generate_value(
            branch=branch,
            leaf=leaf,
            uuid_type=uuid_type,
            variable=variable_name,
            uuid_master=uuid_master,
        )
        _to_replace.append((text[match.start():match.end()], variable_value))

    for pattern, value in _to_replace:
        text = text.replace(pattern, value)

    return text


def apply_variables(text: str, identity_master: IdentityMaster) -> str:
    """Replace variable names with values."""
    variables = re.findall(constants.UUID_VARIABLE_PATTERN, text)

    for with_sign in set(variables):
        variable_name = with_sign[1:]
        variable_value = identity_master.get_value(variable_name)
        text = text.replace(with_sign, variable_value)

    return text


def cast_all(unit: entities.Unit, unit_field: str, entity_field: str,
             sequence: List[str], target_type: Type[CastTypes], **kwargs):
    """Conversion of a collection of simple textual fields."""
    attribute = getattr(unit, unit_field)

    for value in sequence:
        additional = {entity_field: value, **kwargs}
        new_instance = target_type(
            revision=persistent.get_revision(),
            last_update=persistent.get_now(),
            **additional
        )
        attribute.append(new_instance)


def do_themes(source: raw_entities.Source,
              unit: entities.Unit,
              router: Router) -> None:
    """Construct transient entities from ephemeral ones."""
    revision = persistent.get_revision()
    now = persistent.get_now()

    for ep_theme in source.themes:
        cast_all(unit, 'tags_themes', 'value',
                 ep_theme.tags, entities.TagTheme,
                 theme_uuid=ep_theme.uuid)

        tr_theme = entities.Theme(
            revision=revision,
            last_update=now,
            uuid=ep_theme.uuid,
            route=ep_theme.route,
            label=ep_theme.label,
        )
        unit.themes.append(tr_theme)

        router.register_route(tr_theme.uuid, tr_theme.route)


def do_groups(source: raw_entities.Source,
              unit: entities.Unit,
              router: Router,
              identity_master: IdentityMaster,
              uuid_master: UUIDMaster,
              filesystem: infra.Filesystem,
              leaf_folder: str,
              renderer: classes.Renderer) -> None:
    """Construct transient entities from ephemeral ones."""
    for ep_group in source.groups:
        cast_all(unit, 'tags_groups', 'value',
                 ep_group.tags, entities.TagGroup,
                 group_uuid=ep_group.uuid)

        attributes = ep_group.dict()
        attributes.update({
            'revision': persistent.get_revision(),
            'last_update': persistent.get_now(),
            'uuid': ep_group.uuid,
            'theme_uuid': ep_group.theme_uuid,
        })

        tr_group = entities.Group(**attributes)
        unit.groups.append(tr_group)
        router.register_route(tr_group.uuid, tr_group.route)

        if ep_group.route != constants.NO_GROUP:
            preprocess_group_meta_pack(
                unit,
                leaf_folder,
                ep_group,
                identity_master,
                uuid_master,
                filesystem,
                renderer,
                router
            )


def do_synonyms(source: raw_entities.Source, unit: entities.Unit) -> None:
    """Construct transient entities from ephemeral ones."""
    revision = persistent.get_revision()
    now = persistent.get_now()

    for ep_synonym in source.synonyms:
        tr_synonym = entities.Synonym(
            revision=revision,
            last_update=now,
            uuid=ep_synonym.uuid,
            label=ep_synonym.label,
        )
        cast_all(unit, 'synonyms_values', 'value',
                 ep_synonym.values, entities.SynonymValue,
                 synonym_uuid=ep_synonym.uuid)
        unit.synonyms.append(tr_synonym)


def do_no_group_metas(source: raw_entities.Source,
                      unit: entities.Unit,
                      router: Router,
                      identity_master: IdentityMaster,
                      uuid_master: UUIDMaster,
                      filesystem: infra.Filesystem,
                      leaf_folder: str,
                      renderer: classes.Renderer) -> None:
    """Construct transient entities from ephemeral ones."""
    for meta_pack in source.metas:
        preprocess_no_group_meta_pack(unit, leaf_folder, meta_pack,
                                      router, identity_master, uuid_master,
                                      filesystem, renderer)


# pylint: disable=too-many-locals
def preprocess_group_meta_pack(unit: entities.Unit,
                               leaf_folder: str,
                               group: raw_entities.Group,
                               identity_master: IdentityMaster,
                               uuid_master: UUIDMaster,
                               filesystem: infra.Filesystem,
                               renderer: classes.Renderer,
                               router: Router) -> None:
    """Construct transient entities from ephemeral ones."""
    theme_route = router.get_route(group.theme_uuid)

    full_path = filesystem.join(leaf_folder, theme_route, group.route)

    filenames = []
    for filename in filesystem.list_files(full_path):
        name, extension = filesystem.split_extension(filename)
        if not renderer.is_known_media(extension):
            continue

        filenames.append(filename)

    uuids = generate_group_of_uuids(group.uuid, filenames,
                                    identity_master, uuid_master)

    for i, filename in enumerate(filenames, start=1):
        name, ext = filesystem.split_extension(filename)
        file_path = filesystem.join(full_path, f'{name}.{ext}')
        media_info = renderer.analyze(file_path, ext)
        uuid = uuids[group.uuid][filename]

        path_to_content = (
            f'/{constants.MEDIA_CONTENT_FOLDER_NAME}'
            f'/{theme_route}/{group.route}/{uuid}.{ext}'
        )

        path_to_preview = (
            f'/{constants.MEDIA_PREVIEW_FOLDER_NAME}'
            f'/{theme_route}/{group.route}/{uuid}.{ext}'
        )

        if ext == 'gif':
            path_to_thumbnail = (
                f'/{constants.MEDIA_THUMBNAILS_FOLDER_NAME}'
                f'/{theme_route}/{group.route}/{uuid}.gif'
            )
        else:
            path_to_thumbnail = (
                f'/{constants.MEDIA_THUMBNAILS_FOLDER_NAME}'
                f'/{theme_route}/{group.route}/{uuid}.jpg'
            )

        tr_meta = entities.Meta(
            revision=persistent.get_revision(),
            last_update=persistent.get_now(),
            uuid=uuid,
            theme_uuid=group.theme_uuid,
            group_uuid=group.uuid,
            original_filename=name,
            original_extension=ext,
            ordering=i,
            path_to_content=path_to_content,
            path_to_preview=path_to_preview,
            path_to_thumbnail=path_to_thumbnail,
            **media_info,
            author=group.author,
            author_url=group.author_url,
            origin_url=group.origin_url,
            comment=group.comment,
            hierarchy=group.hierarchy,
        )
        unit.metas.append(tr_meta)

        cast_all(unit, 'tags_metas', 'value',
                 group.tags, entities.TagMeta,
                 meta_uuid=uuid)


# pylint: disable=too-many-locals
def preprocess_no_group_meta_pack(unit: entities.Unit,
                                  leaf_folder: str,
                                  ep_meta: raw_entities.Meta,
                                  router: Router,
                                  identity_master: IdentityMaster,
                                  uuid_master: UUIDMaster,
                                  filesystem: infra.Filesystem,
                                  renderer: classes.Renderer) -> None:
    """Construct transient entities from ephemeral ones."""
    theme_route = router.get_route(ep_meta.theme_uuid)
    group_route = router.get_route(ep_meta.group_uuid)

    full_path = filesystem.join(leaf_folder,
                                theme_route,
                                group_route)

    filenames = list(ep_meta.filenames)
    existing_uuids = identity_master.extract_files_cache()
    if ep_meta.group_uuid not in existing_uuids:
        existing_uuids[ep_meta.group_uuid] = {}
    local_uuids = existing_uuids[ep_meta.group_uuid]
    uuids = generate_group_of_uuids_from_scratch(filenames, local_uuids,
                                                 uuid_master)
    existing_uuids[ep_meta.group_uuid].update(uuids)
    identity_master.add_files_cache(existing_uuids)

    for filename in ep_meta.filenames:
        name, ext = filesystem.split_extension(filename)
        file_path = filesystem.join(full_path, filename)
        media_info = renderer.analyze(file_path, ext)
        uuid = existing_uuids[ep_meta.group_uuid][filename]

        path_to_content = (
            f'/{constants.MEDIA_CONTENT_FOLDER_NAME}'
            f'/{theme_route}/{group_route}/{uuid}.{ext}'
        )

        path_to_preview = (
            f'/{constants.MEDIA_PREVIEW_FOLDER_NAME}'
            f'/{theme_route}/{group_route}/{uuid}.{ext}'
        )

        if ext == 'gif':
            path_to_thumbnail = (
                f'/{constants.MEDIA_THUMBNAILS_FOLDER_NAME}'
                f'/{theme_route}/{group_route}/{uuid}.gif'
            )
        else:
            path_to_thumbnail = (
                f'/{constants.MEDIA_THUMBNAILS_FOLDER_NAME}'
                f'/{theme_route}/{group_route}/{uuid}.jpg'
            )

        tr_meta = entities.Meta(
            revision=persistent.get_revision(),
            last_update=persistent.get_now(),
            uuid=uuid,
            theme_uuid=ep_meta.theme_uuid,
            group_uuid=ep_meta.group_uuid,
            original_filename=name,
            original_extension=ext,
            ordering=0,
            path_to_content=path_to_content,
            path_to_preview=path_to_preview,
            path_to_thumbnail=path_to_thumbnail,
            **media_info,
            author=ep_meta.author,
            author_url=ep_meta.author_url,
            origin_url=ep_meta.origin_url,
            comment=ep_meta.comment,
            hierarchy=ep_meta.hierarchy,
        )
        unit.metas.append(tr_meta)

        cast_all(unit, 'tags_metas', 'value',
                 ep_meta.tags, entities.TagMeta,
                 meta_uuid=uuid)


def generate_group_of_uuids(group_uuid: str,
                            filenames: List[str],
                            identity_master: IdentityMaster,
                            uuid_master: UUIDMaster
                            ) -> Dict[str, Dict[str, str]]:
    """Create complete and correctly ordered map with uuid for each file."""
    filenames.sort()
    existing_uuids = identity_master.extract_files_cache()
    local_uuids = existing_uuids.get(group_uuid, {})

    if local_uuids:
        uuids = generate_group_of_uuids_with_insertion(filenames,
                                                       local_uuids,
                                                       uuid_master)
    else:
        uuids = generate_group_of_uuids_from_scratch(filenames,
                                                     local_uuids,
                                                     uuid_master)
    existing_uuids[group_uuid] = {**local_uuids, **uuids}
    identity_master.add_files_cache(existing_uuids)
    return existing_uuids


def generate_group_of_uuids_from_scratch(filenames: List[str],
                                         local_uuids: Dict[str, str],
                                         uuid_master: UUIDMaster
                                         ) -> Dict[str, str]:
    """Generate random UUIDs and sort."""
    uuids = []
    for filename in filenames:
        uuid = local_uuids.get(filename)
        if uuid is None:
            uuid = uuid_master.generate_uuid_meta()
            uuids.append(uuid)

    uuids.sort()
    return dict(zip(filenames, uuids))


def generate_group_of_uuids_with_insertion(filenames: List[str],
                                           local_uuids: Dict[str, str],
                                           uuid_master: UUIDMaster
                                           ) -> Dict[str, str]:
    """Generate UUIDs in a way the will follow existing order."""
    uuids_list = [None] * len(filenames)

    for i, filename in enumerate(filenames):
        uuids_list[i] = local_uuids.get(filename)

    if None not in uuids_list:
        return local_uuids

    def scan(go_left: bool, index: int) -> Optional[str]:
        """Return first non empty element or None."""
        if index == 0:
            return uuids_list[0]

        if index == len(uuids_list) - 1:
            return uuids_list[index - 1]

        return scan(go_left, index + (-1 if go_left else 1))

    for i, uuid in enumerate(uuids_list):
        if uuid is not None:
            continue

        if i == 0:
            new_uuid = _generate_uuid_relatively(operator.lt,
                                                 min(local_uuids.values()),
                                                 uuid_master)
        elif i == len(filenames) - 1:
            new_uuid = _generate_uuid_relatively(operator.gt,
                                                 max(local_uuids.values()),
                                                 uuid_master)
        else:
            left = scan(True, i)
            right = scan(False, i)
            assert left is not None

            if right is None:
                new_uuid = _generate_uuid_relatively(
                    operator.gt, max(local_uuids.values()), uuid_master)
            else:
                new_uuid = _generate_uuid_between(left, right, uuid_master)

        uuids_list[i] = new_uuid
        uuid_master.add_existing_uuid(new_uuid)

    assert None not in uuids_list
    return dict(zip(filenames, map(str, uuids_list)))


def _generate_uuid_relatively(compare: Callable, reference: str,
                              uuid_master: UUIDMaster) -> str:
    """Create UUID bigger or smaller than this one."""
    new_uuid = f'{constants.PREFIX_META}_{uuid_master.generate_uuid()}'
    while not compare(new_uuid, reference):
        new_uuid = f'{constants.PREFIX_META}_{uuid_master.generate_uuid()}'
    return new_uuid


def _generate_uuid_between(left: str, right: str,
                           uuid_master: UUIDMaster) -> str:
    """Create UUID between two existing."""
    new_uuid = f'{constants.PREFIX_META}_{uuid_master.generate_uuid()}'
    while not (left < new_uuid < right):
        new_uuid = f'{constants.PREFIX_META}_{uuid_master.generate_uuid()}'
    return new_uuid
