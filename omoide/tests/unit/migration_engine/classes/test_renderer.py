# -*- coding: utf-8 -*-

"""Tests.
"""
import pytest

from omoide.migration_engine.classes.class_renderer import Renderer


@pytest.fixture
def renderer_instance():
    return Renderer()


def test_renderer_calculate_size_from_zero(renderer_instance):
    with pytest.raises(ValueError):
        renderer_instance.calculate_size(0, 1, 2, 3)


def test_renderer_calculate_size_square(renderer_instance):
    width, height = 1024, 1024
    res = renderer_instance.calculate_size(width, height, 512, 512)
    ref = (512, 512)
    assert res == ref


def test_renderer_calculate_size_portrait(renderer_instance):
    width, height = 256, 1024
    res = renderer_instance.calculate_size(width, height, 512, 512)
    ref = (128, 512)
    assert res == ref


def test_renderer_calculate_size_album(renderer_instance):
    width, height = 1024, 256
    res = renderer_instance.calculate_size(width, height, 512, 512)
    ref = (1024, 256)
    assert res == ref


def test_renderer_calculate_size_realistic(renderer_instance):
    width, height = 3782, 2743
    res = renderer_instance.calculate_size(width, height, 512, 512)
    ref = (706, 512)
    assert res == ref
