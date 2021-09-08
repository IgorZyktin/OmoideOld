# -*- coding: utf-8 -*-

"""Tests.
"""

from omoide.migration_engine.operations.unite import UUIDMaster, IdentityMaster
from omoide.migration_engine.operations.unite import preprocessing


# def test_uuid_insertion_with_ends():
#     # arrange
#     uuid_master = UUIDMaster()
#     identity_master = IdentityMaster()
#     filenames = [
#         'file1.txt',
#         'file2.txt',
#         'file3.txt',
#         'file4.txt',
#         'file5.txt',
#         'file6.txt',
#     ]
#
#     existing_uuids = {
#         'file1.txt': 'm_8bae358c-29cc-464c-bd2b-b524f40fa059',
#         'file3.txt': 'm_c74af179-7e5e-4d9c-ba0f-87dea314d676',
#         'file6.txt': 'm_e5d4448a-8ea9-464d-93d8-83551665e389',
#     }
#     identity_master.add_files_cache(existing_uuids)
#
#     # act
#     uuids = preprocessing.generate_group_of_uuids(
#         filenames, identity_master, uuid_master)
#
#     # assert
#     by_filename = sorted(uuids.items(), key=lambda x: x[0])
#     by_uuid = sorted(uuids.items(), key=lambda x: x[0])
#     assert by_filename == by_uuid
#
#
# def test_uuid_insertion_without_ends():
#     # arrange
#     uuid_master = UUIDMaster()
#     identity_master = IdentityMaster()
#     filenames = [
#         'file1.txt',
#         'file2.txt',
#         'file3.txt',
#         'file4.txt',
#         'file5.txt',
#         'file6.txt',
#     ]
#
#     existing_uuids = {
#         'file2.txt': 'm_8bae358c-29cc-464c-bd2b-b524f40fa059',
#         'file5.txt': 'm_e5d4448a-8ea9-464d-93d8-83551665e389',
#     }
#     identity_master.add_files_cache(existing_uuids)
#
#     # act
#     uuids = preprocessing.generate_group_of_uuids(
#         filenames, identity_master, uuid_master)
#
#     # assert
#     by_filename = sorted(uuids.items(), key=lambda x: x[0])
#     by_uuid = sorted(uuids.items(), key=lambda x: x[0])
#     assert by_filename == by_uuid
#
#
# def test_uuid_insertion_nothing():
#     # arrange
#     uuid_master = UUIDMaster()
#     identity_master = IdentityMaster()
#     filenames = [
#         'file1.txt',
#         'file2.txt',
#         'file3.txt',
#         'file4.txt',
#         'file5.txt',
#         'file6.txt',
#     ]
#
#     existing_uuids = {}
#     identity_master.add_files_cache(existing_uuids)
#
#     # act
#     uuids = preprocessing.generate_group_of_uuids(
#         filenames, identity_master, uuid_master)
#
#     # assert
#     by_filename = sorted(uuids.items(), key=lambda x: x[0])
#     by_uuid = sorted(uuids.items(), key=lambda x: x[0])
#     assert by_filename == by_uuid
#
#
# def test_uuid_insertion_one():
#     # arrange
#     uuid_master = UUIDMaster()
#     identity_master = IdentityMaster()
#     filenames = [
#         'file1.txt',
#         'file2.txt',
#         'file3.txt',
#         'file4.txt',
#         'file5.txt',
#         'file6.txt',
#     ]
#
#     existing_uuids = {
#         'file2.txt': 'm_8bae358c-29cc-464c-bd2b-b524f40fa059',
#     }
#     identity_master.add_files_cache(existing_uuids)
#
#     # act
#     uuids = preprocessing.generate_group_of_uuids(
#         filenames, identity_master, uuid_master)
#
#     # assert
#     by_filename = sorted(uuids.items(), key=lambda x: x[0])
#     by_uuid = sorted(uuids.items(), key=lambda x: x[0])
#     assert by_filename == by_uuid
