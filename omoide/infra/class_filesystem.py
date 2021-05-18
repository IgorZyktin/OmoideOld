# -*- coding: utf-8 -*-

"""Abstraction of filesystem.
"""
import os
import shutil
import typing
from pathlib import Path
from typing import List, Tuple, Optional

import ujson

from omoide.infra.class_stdout import STDOut

__all__ = [
    'Filesystem',
]


class Filesystem:
    """Abstraction of filesystem.
    """

    @staticmethod
    def split_extension(filename: str) -> Tuple[str, str]:
        """Return name and extension of the file."""
        name, extension = os.path.splitext(filename)
        return name, extension.lstrip('.')

    @staticmethod
    def exists(path: str) -> bool:
        """Return True if object exists."""
        return os.path.exists(path)

    @staticmethod
    def not_exists(path: str) -> bool:
        """Return True if object not exists."""
        return not os.path.exists(path)

    @staticmethod
    def read_file(path: str) -> str:
        """Read textual file from the disk."""
        with open(path, mode='r', encoding='utf-8') as file:
            content = file.read()
        return content

    @staticmethod
    def write_file(path: str, content: str) -> None:
        """Write textual file to the disk."""
        with open(path, mode='w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def read_json(path: str) -> dict:
        """Read json file from the disk."""
        with open(path, mode='r', encoding='utf-8') as file:
            content = ujson.load(file)
        return content

    @staticmethod
    def write_json(path: str, content: typing.Union[dict, list]) -> None:
        """Write json file to the disk."""
        with open(path, mode='w', encoding='utf-8') as file:
            ujson.dump(content, file, indent=4, ensure_ascii=False)

    @staticmethod
    def join(*args) -> str:
        """Join path for specific filesystem."""
        return os.path.join(*args)

    @staticmethod
    def cut_tail(path: str) -> str:
        """Return path without last element."""
        result, _ = path.rsplit(os.sep, maxsplit=1)
        return result

    @staticmethod
    def listdir(path: str) -> List[str]:
        """Enlist all entries in given directory."""
        return os.listdir(path)

    @classmethod
    def list_files(cls, path: str) -> List[str]:
        """Enlist all files in given directory."""
        return [
            x for x in cls.listdir(path)
            if os.path.isfile(os.path.join(path, x))
        ]

    @classmethod
    def list_folders(cls, path: str) -> List[str]:
        """Enlist all folders in given directory."""
        return [
            x for x in cls.listdir(path)
            if os.path.isdir(os.path.join(path, x))
        ]

    @staticmethod
    def absolute(path: str) -> str:
        """Return absolute path."""
        return os.path.abspath(path)

    @classmethod
    def ensure_folder_exists(cls, directory: str,
                             stdout: Optional[STDOut] = None,
                             prefix: str = '') -> bool:
        """Create all chain of folders at given path.

        Return True if creation is successful.
        Do not give path to files to this method!
        """
        _path = Path(directory)
        parts = list(_path.parts)
        current_path = None
        actually_created = False

        for part in parts:
            if current_path is None:
                current_path = part
            else:
                current_path = cls.join(current_path, part)

            if not os.path.exists(current_path):
                cls.create_directory(current_path)
                actually_created = True

                if stdout:
                    stdout.light_green(
                        f'{prefix}New folder created: {current_path}'
                    )

        return actually_created

    @staticmethod
    def copy_file(source_path: str, target_path: str) -> None:
        """Copy file from source to target."""
        shutil.copy(source_path, target_path)

    @staticmethod
    def move_file(source_path: str, target_path: str) -> None:
        """Move file from source to target."""
        shutil.move(source_path, target_path)

    @staticmethod
    def delete_file(target_path: str) -> None:
        """Delete file."""
        os.remove(target_path)

    @staticmethod
    def create_directory(target_path: str) -> None:
        """Create directory."""
        os.mkdir(target_path)
