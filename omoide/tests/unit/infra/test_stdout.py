# -*- coding: utf-8 -*-

"""Tests.
"""

from unittest import mock

import pytest

from omoide import infra


@pytest.mark.parametrize('method_name, color_name', [
    ('light_green', 'LIGHTGREEN_EX'),
    ('green', 'GREEN'),
    ('yellow', 'YELLOW'),
    ('red', 'RED'),
    ('gray', 'LIGHTBLACK_EX'),
    ('magenta', 'MAGENTA'),
    ('cyan', 'CYAN'),
])
def test_stdout_colored(method_name, color_name):
    stdout = infra.STDOut()
    method = getattr(stdout, method_name)
    with mock.patch('omoide.infra.class_stdout.print') as fake_print:
        with mock.patch('omoide.infra.class_stdout.Fore') as fake_fore:
            setattr(fake_fore, 'RESET', f'<reset>')
            setattr(fake_fore, color_name, f'<{method_name}>')
            method('something')
            fake_print.assert_called_once_with(
                f'<{method_name}>something', end='<reset>\n')


def test_stdout_not_colored():
    stdout = infra.STDOut()
    with mock.patch('omoide.infra.class_stdout.print') as fake_print:
        stdout.print('something')
        fake_print.assert_called_once_with('something', end='\n')
