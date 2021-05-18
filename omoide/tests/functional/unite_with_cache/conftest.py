# -*- coding: utf-8 -*-

"""Tests.
"""

import pytest


@pytest.fixture
def unite_with_cache_folder_structure():
    """Template for folders."""
    return {
        'source_1': [
            'migration_1',
            'migration_2',
        ],
        'source_2': [
            'migration_3',
            'migration_4'
        ]
    }


@pytest.fixture
def unite_with_cache_sources():
    """Template for source files."""
    return {
        ('source_1', 'migration_1'): {
            'themes': [
                {
                    'uuid': "var('t', 'probe_theme')",
                    'route': 'probe',
                    'label': 'Probe theme',
                    'tags': [
                        'probe'
                    ]
                }
            ],
            'groups': [
                {
                    'uuid': "var('g', 'some_group')",
                    'theme_uuid': '$probe_theme',
                    'route': 'some',
                    'label': 'Some group'
                }
            ],
        },
        ('source_1', 'migration_2'): {
            'groups': [
                {
                    'uuid': "var('g', 'not_really_a_group')",
                    'theme_uuid': '$probe_theme',
                    'route': 'no_group',
                    'label': 'No specific group'
                }
            ],
            'metas': [
                {
                    'theme_uuid': "$probe_theme",
                    'group_uuid': '$not_really_a_group',
                    'filenames': [
                        'file4.test',
                        'file5.test',
                        'file6.test',
                    ],
                    'tags': [
                        'tag1'
                    ]
                },
            ]
        },
        ('source_2', 'migration_3'): {
            'metas': [
                {
                    'theme_uuid': "$probe_theme",
                    'group_uuid': '$not_really_a_group',
                    'filenames': [
                        'file7.test',
                        'file8.test',
                    ],
                    'tags': [
                        'tag2'
                    ]
                },
            ]
        },
        ('source_2', 'migration_4'): {
            'groups': [
                {
                    'uuid': "var('g', 'other_group')",
                    'theme_uuid': '$probe_theme',
                    'route': 'other',
                    'label': 'Other group'
                }
            ],
        },
    }


@pytest.fixture
def unite_with_cache_caches():
    """Template for cache files."""
    return {
        ('source_1', 'migration_1'): {
            'variables': {
                'themes': {
                    'probe_theme': 't_650b7cdb-bd34-4626-95f7-be5d5b8ae74f'
                },
                'synonyms': {},
                'groups': {
                    'some_group': 'g_1917972e-c259-4db8-8586-6c3e79f8f517'
                },
                'metas': {}
            },
            'uuids': [
                '763c24a3-a294-4bfe-ac46-a711daf8553f',
                '5cb7589c-bd0c-45b4-a62a-d66f94d9de94',
                '808a6ad7-795a-47f8-9b17-519e9e393974'
            ]
        },
        ('source_1', 'migration_2'): {},
        ('source_2', 'migration_3'): {
            'variables': {
                'themes': {},
                'synonyms': {},
                'groups': {},
                'metas': {}
            },
            'uuids': [
                '9096d192-3dda-40ec-80e0-e2874a984b6a',
                '1438ffc2-6455-4da4-80ad-c48a6ca60455'
            ]
        },
        ('source_2', 'migration_4'): {},
    }


@pytest.fixture
def unite_with_cache_media_files():
    """Template for pseudo images files."""
    return {
        ('source_1', 'migration_1', 'probe', 'some'): [
            'file1.test',
            'file2.test',
            'file3.test',
        ],
        ('source_1', 'migration_2', 'probe', 'no_group'): [
            'file4.test',
            'file5.test',
            'file6.test',
        ],
        ('source_2', 'migration_3', 'probe', 'no_group'): [
            'file7.test',
            'file8.test',
        ],
        ('source_2', 'migration_4', 'probe', 'other'): [
            'file9.test',
        ],
    }
