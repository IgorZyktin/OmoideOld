# -*- coding: utf-8 -*-

"""Base components for all singletons.
"""
__all__ = [
    'SingletonMeta',
]


class SingletonMeta(type):
    """Singleton metaclass."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Create or get an instance."""
        if cls not in cls._instances:
            cls._instances[cls] = cls._new_instance(*args, **kwargs)
        return cls._instances[cls]

    def clear_instances(cls):
        """Remove all stored instances."""
        cls._instances.clear()

    def _new_instance(cls, *args, **kwargs):
        """Generic object creation."""
        return super(SingletonMeta, cls).__call__(*args, **kwargs)
