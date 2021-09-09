# -*- coding: utf-8 -*-

"""Specific generation of UUIDs for bulk operations.
"""
from typing import MutableSequence, Optional, TypeVar, Callable

T = TypeVar('T')
Sparse = MutableSequence[Optional[T]]

MIN_UUID_VALUE = 'm_00000000-0000-0000-0000-000000000000'
MAX_UUID_VALUE = 'm_ffffffff-ffff-ffff-ffff-ffffffffffff'


def generate_value(minimum: T, maximum: T, generator: Callable[[], T]) -> T:
    """Generate new random value between two given examples."""
    new_value = generator()
    while not (minimum < new_value < maximum):
        new_value = generator()
    return new_value


def fill_array_inplace(array: Sparse, minimum: T,
                       maximum: T, generator: Callable[[], T]) -> None:
    """Put appropriate random values if array has holes.

    Basic examples:
        [None, 5, 7] -> [1, 5, 7]
        [None, 5, None, 9, None] -> [4, 5, 7, 87635]
    """
    start = 0
    for i in range(0, len(array)):
        element = array[i]
        if element is not None:
            for j in range(start, i):
                new_value = generate_value(minimum, element, generator)
                minimum = new_value
                array[j] = new_value

            start = i + 1
            minimum = max(minimum, element)

    for k in range(start, len(array)):
        new_value = generate_value(minimum, maximum, generator)
        minimum = new_value
        array[k] = new_value
