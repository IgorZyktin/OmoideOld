# -*- coding: utf-8 -*-
"""Display folder tree.
"""
from collections import defaultdict

from omoide import commands
from omoide import infra


def act(command: commands.ShowTreeCommand,
        filesystem: infra.Filesystem,
        stdout: infra.STDOut) -> int:
    """Display folder tree."""
    walk = infra.walk_sources_from_command(command, filesystem)
    tree = defaultdict(list)

    total = 0
    for branch, leaf, _ in walk:
        tree[branch].append(leaf)
        total += 1

    for i, (branch, leaves) in enumerate(tree.items(), start=1):
        stdout.print(f'{i}. {branch}')
        for j, leaf in enumerate(sorted(leaves), start=1):
            stdout.print(f'\t{j}. {leaf}')

    return total
