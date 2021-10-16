# -*- coding: utf-8 -*-

"""Textual preprocessing components.
"""
import re
from typing import Union, List, Type, Tuple, Dict, cast

from omoide import constants
from omoide.infra import walking
from omoide.migration_engine import classes, entities
from omoide.migration_engine.operations.unite import persistent, raw_entities
from omoide.migration_engine.operations.unite import uuid_filling
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

    for placeholder, value in _to_replace:
        text = text.replace(placeholder, value)

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
              bottom: walking.Bottom,
              unit: entities.Unit,
              router: Router,
              identity_master: IdentityMaster,
              uuid_master: UUIDMaster,
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
                bottom,
                ep_group,
                identity_master,
                uuid_master,
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
                      bottom: walking.Bottom,
                      unit: entities.Unit,
                      router: Router,
                      identity_master: IdentityMaster,
                      uuid_master: UUIDMaster,
                      renderer: classes.Renderer) -> None:
    """Construct transient entities from ephemeral ones."""
    for meta_pack in source.metas:
        preprocess_no_group_meta_pack(unit, bottom, meta_pack,
                                      router, identity_master, uuid_master,
                                      renderer)


# pylint: disable=too-many-locals
def preprocess_group_meta_pack(unit: entities.Unit,
                               bottom: walking.Bottom,
                               group: raw_entities.Group,
                               identity_master: IdentityMaster,
                               uuid_master: UUIDMaster,
                               renderer: classes.Renderer,
                               router: Router) -> None:
    """Construct transient entities from ephemeral ones."""
    theme_route = router.get_route(group.theme_uuid)

    full_path = bottom.filesystem.join(bottom.leaf_folder,
                                       theme_route,
                                       group.route)

    filenames = []
    for filename in bottom.filesystem.list_files(full_path):
        name, extension = bottom.filesystem.split_extension(filename)
        if not renderer.is_known_media(extension):
            continue

        filenames.append(filename)

    uuids = generate_group_of_uuids(group.uuid, filenames,
                                    identity_master, uuid_master)

    for i, filename in enumerate(filenames, start=1):
        name, ext = bottom.filesystem.split_extension(filename)
        file_path = bottom.filesystem.join(full_path, f'{name}.{ext}')
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
                                  bottom: walking.Bottom,
                                  ep_meta: raw_entities.Meta,
                                  router: Router,
                                  identity_master: IdentityMaster,
                                  uuid_master: UUIDMaster,
                                  renderer: classes.Renderer) -> None:
    """Construct transient entities from ephemeral ones."""
    theme_route = router.get_route(ep_meta.theme_uuid)
    group_route = router.get_route(ep_meta.group_uuid)

    full_path = bottom.filesystem.join(bottom.leaf_folder,
                                       theme_route,
                                       group_route)

    uuids = generate_group_of_uuids(ep_meta.group_uuid,
                                    list(ep_meta.filenames),
                                    identity_master, uuid_master)

    for filename in ep_meta.filenames:
        name, ext = bottom.filesystem.split_extension(filename)
        file_path = bottom.filesystem.join(full_path, filename)
        media_info = renderer.analyze(file_path, ext)
        uuid = uuids[ep_meta.group_uuid][filename]

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

    def generator() -> uuid_filling.T:
        """Create new UUID value."""
        return f'{constants.PREFIX_META}_{uuid_master.generate_uuid()}'

    if not local_uuids:
        uuids_list = [uuid_master.generate_uuid_meta() for _ in filenames]
        uuids_list.sort()

    else:
        uuids_list = [None] * len(filenames)
        for i, filename in enumerate(filenames):
            uuids_list[i] = local_uuids.get(filename)

        uuid_filling.fill_array_inplace(
            array=uuids_list,
            minimum=uuid_filling.MIN_UUID_VALUE,
            maximum=uuid_filling.MAX_UUID_VALUE,
            generator=generator,
        )
        assert None not in uuids_list
        uuids_list = cast(List[str], uuids_list)

    existing_uuids[group_uuid] = {**local_uuids,
                                  **dict(zip(filenames, uuids_list))}
    identity_master.add_files_cache(existing_uuids)
    uuid_master.add_existing_uuids()
    return existing_uuids
