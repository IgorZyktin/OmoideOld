# -*- coding: utf-8 -*-

"""Script that splits files to folders after their conversion from PDF.
"""
import os

TARGET_FOLDER = 'D:\\BGC_ARCHIVE_QUEUE9'


def main() -> None:
    """Entry point."""
    files = os.listdir(TARGET_FOLDER)
    for filename in files:
        if os.path.isdir(os.path.join(TARGET_FOLDER, filename)):
            continue
        original_name, _, number = filename.rsplit('_', maxsplit=2)
        original_name = original_name.lower().replace(' ', '_')
        folder = os.path.join(TARGET_FOLDER, original_name)

        if not os.path.exists(folder):
            print('created', folder)
            os.mkdir(folder)

        target_path = os.path.join(folder, f'{original_name}_{number}')
        if os.path.exists(target_path):
            raise FileExistsError(target_path)

        os.rename(
            os.path.join(TARGET_FOLDER, filename),
            os.path.join(folder, f'{original_name}_{number}')
        )


if __name__ == '__main__':
    main()
