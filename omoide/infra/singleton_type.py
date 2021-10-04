# -*- coding: utf-8 -*-

"""Base components for all singletons.
"""
__all__ = [
    'SingletonMeta',
]


class SingletonMeta(type):
    """Singleton metaclass."""
    _instances = {}
    _sentinel = object()

    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict):
        """Create the class itself."""
        mcs.mutate_attrs(attrs)
        cls = super().__new__(mcs, name, bases, attrs)
        return cls

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

    @classmethod
    def mutate_attrs(mcs, attrs: dict) -> None:
        """Insert descriptors into class."""
        for attr_name in attrs['__annotations__']:
            def __get__(instance, owner=None):
                value = getattr(instance, f'_{attr_name}', mcs._sentinel)
                if value is mcs._sentinel:
                    raise AttributeError(
                        f'Attribute {attr_name!r} was never set'
                    )
                return value

            def __set__(instance, value):
                setattr(instance, f'_{attr_name}', value)

            attrs[attr_name] = property(__get__, __set__)
