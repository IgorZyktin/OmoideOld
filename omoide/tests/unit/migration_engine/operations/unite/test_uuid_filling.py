# -*- coding: utf-8 -*-

"""Tests.
"""
import pytest

from omoide.migration_engine.operations.unite import UUIDMaster, IdentityMaster
from omoide.migration_engine.operations.unite import preprocessing

UUID_FILLING_FILENAMES = [
    'file1.txt',
    'file2.txt',
    'file3.txt',
    'file4.txt',
    'file5.txt',
    'file6.txt',
]

UUID_FILLING_EXISTING_UUIDS_HOLES = {
    'file1.txt': 'm_8bae358c-29cc-464c-bd2b-b524f40fa059',
    'file2.txt': None,
    'file3.txt': 'm_c74af179-7e5e-4d9c-ba0f-87dea314d676',
    'file4.txt': None,
    'file5.txt': None,
    'file6.txt': 'm_e5d4448a-8ea9-464d-93d8-83551665e389',
}

UUID_FILLING_EXISTING_UUIDS_ALL = {
    'file1.txt': 'm_6021c453-a61e-4718-9af1-9081db294f1c',
    'file2.txt': 'm_8bae358c-29cc-464c-bd2b-b524f40fa059',
    'file3.txt': 'm_c74af179-7e5e-4d9c-ba0f-87dea314d676',
    'file4.txt': 'm_df43b43a-3527-417d-9fe9-44d572b23ee6',
    'file5.txt': 'm_e3edaf77-7c9b-45b7-bff5-72e79734f208',
    'file6.txt': 'm_e5d4448a-8ea9-464d-93d8-83551665e389',
}

UUID_FILLING_EXISTING_UUIDS_None = {
    'file1.txt': None,
    'file2.txt': None,
    'file3.txt': None,
    'file4.txt': None,
    'file5.txt': None,
    'file6.txt': None,
}

UUID_FILLING_EXISTING_UUIDS_ENDS = {
    'file1.txt': None,
    'file2.txt': 'm_8bae358c-29cc-464c-bd2b-b524f40fa059',
    'file3.txt': 'm_c74af179-7e5e-4d9c-ba0f-87dea314d676',
    'file4.txt': 'm_df43b43a-3527-417d-9fe9-44d572b23ee6',
    'file5.txt': 'm_e3edaf77-7c9b-45b7-bff5-72e79734f208',
    'file6.txt': None,
}


@pytest.mark.parametrize('filenames, uuids', [
    (UUID_FILLING_FILENAMES, UUID_FILLING_EXISTING_UUIDS_HOLES),
    (UUID_FILLING_FILENAMES, UUID_FILLING_EXISTING_UUIDS_ALL),
    (UUID_FILLING_FILENAMES, UUID_FILLING_EXISTING_UUIDS_None),
    (UUID_FILLING_FILENAMES, UUID_FILLING_EXISTING_UUIDS_ENDS),
])
def test_uuid_filling_with_holes(filenames, uuids):
    # arrange
    uuid_master = UUIDMaster()
    identity_master = IdentityMaster()
    identity_master.add_files_cache({'test_group': uuids})

    # act
    out_uuids = preprocessing.generate_group_of_uuids(
        'test_group', filenames, identity_master, uuid_master)

    # assert
    by_filename = sorted(out_uuids.items(), key=lambda x: x[0])
    by_uuid = sorted(out_uuids.items(), key=lambda x: x[0])
    assert by_filename == by_uuid
