#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Property implementations.

====

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__all__ = 'T', 'SLOTTED_PREFIX', 'ReadOnlyProperty', 'cached_property', 'ClassType',

import enum
import inspect
from typing import Awaitable, Any, Callable, Generic, Type, TypeVar, Union

T = TypeVar('T')

# We use this instead of `_` as it allows properties with names prefixed by
# an underscore to now have to mess around with namespace mangling. For example,
# without this, a property called `_foo` would look to an attribute called
# `__foo`, however, this would upon declaration in slots be renamed to
# `_Klass__foo` due to mangling convention.
SLOTTED_PREFIX = '_p_'


class ReadOnlyProperty:
    """Read only property that just wraps a supplier method."""
    __slots__ = 'func',

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is not None:
            return self.func(instance)
        else:
            return self

    def __str__(self):
        return str(self.func())

    def __repr__(self):
        return repr(self.func())


# noinspection PyMethodOverriding
class ClassProperty:
    """
    Property that latches on as a class method. This must still be accessed
    from an object if you expect it to behave correctly.
    """
    __slots__ = 'func',

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        instance = type(instance) if instance else owner
        return self.func(instance)


@enum.unique
class ClassType(enum.Enum):
    """Valid class declaration implementations."""
    DICT = enum.auto()
    SLOTS = enum.auto()


def cached_property(class_type: Union[ClassType, str] = ClassType.DICT):
    """
    Generates a decorator for a method that makes it into a cached property.

    Parameters
    ----------
        class_type:
            The class attribute container type. Generally this is ``DICT``
            (default). If you implement ``__slots__`` in the class and/or all
            base types, then you need to use ``SLOTS``.

    Note
    ----
        All cached property values should have a corresponding slotted attribute
        with the same name, preceded with ``_p_``.
        Slotted cached properties with a name ``foo`` would expect a slot called
        ``_p_foo`` to exist.

    Returns
    -------
        A decorator for a callable.
    """
    if isinstance(class_type, str):
        class_type = ClassType[class_type]

    if not isinstance(class_type, ClassType):
        raise TypeError(f'Decorator argument should be ClassType or str, not {class_type.__name__}')

    def wrapper(func):
        is_coro = inspect.iscoroutinefunction(func)

        if class_type == class_type.DICT:
            class_ = AsyncCachedProp if is_coro else InstanceCachedProp
        elif class_type == class_type.SLOTS:
            class_ = AsyncSlottedCachedProp if is_coro else SlottedCachedProp
        else:
            raise NotImplementedError(f'{class_type} is not supported.')

        return class_(func)

    return wrapper


class CachedProperty(object):
    """
    Cached property base type.

    Enables nicer type checking. ``if isinstance(foo, CachedProperty)`` is then true fo
    """
    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        if cls is CachedProperty:
            raise TypeError('Abstract slotted class cannot be instantiated.')
        else:
            return super().__new__(cls, *args, **kwargs)

    def __get__(self, instance, owner):
        ...

    def __delete__(self, instance):
        ...


class InstanceCachedProp(CachedProperty, Generic[T]):
    """
    A cached property type.
    """
    __slots__ = 'func',

    def __init__(self, func: Callable[[Any], T]):
        self.func = func

    @property
    def __name__(self) -> str:
        """Returns the cache name."""
        return self.func.__name__ or self.func.__qualname__

    def __get__(self, instance: Any, owner: Type) -> T:
        """
        Get the property's cached value, or compute and cache it if it
        is not already cached.

        Parameters
        ----------
            instance:
                the instance we are a descriptor for.
            owner:
                the owner type of the instance.

        Returns
        -------
            the cached value.
        """
        if instance is not None:
            try:
                return instance.__dict__[self.__name__]
            except KeyError:
                return instance.__dict__.setdefault(self.__name__, self.func(instance))
        else:
            return self

    def __delete__(self, instance: object):
        """
        Clears the attribute value from the cache, if it exists.

        Parameters
        ----------
            instance:
                the object instance we are a descriptor for.
        """
        instance.__dict__.pop(self.__name__, None)


class SlottedCachedProp(CachedProperty, Generic[T]):
    """
    A cached property type for slotted instances. This will look for a slot with the
    same name, but preceded by an underscore.
    """
    __slots__ = 'func',

    def __init__(self, func: Callable[[Any], T]):
        self.func = func

    @property
    def __name__(self) -> str:
        """Returns the slot name."""
        return f'{SLOTTED_PREFIX}{self.func.__name__ or self.func.__qualname__}'

    def __get__(self, instance: Any, owner: Type) -> T:
        """
        Get the property's cached value, or compute and cache it if it
        is not already cached.

        Parameters
        ----------
            instance:
                the instance we are a descriptor for.
            owner:
                the owner type of the instance.

        Returns
        -------
            the cached value.
        """
        if instance is not None:
            try:
                return getattr(instance, self.__name__)
            except AttributeError:
                val = self.func(instance)
                setattr(self.func, self.__name__, val)
                return val
        else:
            return self

    def __delete__(self, instance: object):
        """
        Clears the attribute value from the cache, if it exists.

        Parameters
        ----------
            instance:
                the object instance we are a descriptor for.
        """
        try:
            delattr(instance, self.__name__)
        except AttributeError:
            pass


class AsyncCachedProp(CachedProperty, Generic[T]):
    """
    A cached property type that must be awaited.
    """
    __slots__ = 'func',

    def __init__(self, func: Callable[[Any], T]):
        self.func = func

    @property
    def __name__(self):
        """Returns the cache name."""
        return self.func.__name__ or self.func.__qualname__

    def __get__(self, instance: Any, owner: Type) -> Awaitable[T]:
        """
        Get the property's cached value, or compute and cache it if it
        is not already cached.

        Parameters
        ----------
            instance:
                the instance we are a descriptor for.
            owner:
                the owner type of the instance.
        Returns
        -------
            a coroutine to be awaited to retrieve the cached value.
        """
        return self.__aget(instance, owner)

    async def __aget(self, instance: Any, _: Type) -> T:
        if instance is not None:
            try:
                return instance.__dict__[self.__name__]
            except KeyError:
                return instance.__dict__.setdefault(self.__name__, self.func(instance))
        else:
            return self

    def __delete__(self, instance: Any):
        """
        Clears the attribute value from the cache, if it exists.

        Parameters
        ----------
            instance:
                the object instance we are a descriptor for.
        """
        instance.__dict__.pop(self.__name__, None)


class AsyncSlottedCachedProp(CachedProperty, Generic[T]):
    """
    An async cached property type for slotted instances. This will look for a
    slot with the same name, but preceded by an underscore, and must be awaited.
    """
    __slots__ = 'func',

    def __init__(self, func: Callable[[Any], T]):
        self.func = func

    @property
    def __name__(self) -> str:
        """Returns the slot name."""
        return f'{SLOTTED_PREFIX}{self.func.__name__ or self.func.__qualname__}'

    def __get__(self, instance: Any, owner: Type) -> Awaitable[T]:
        """
        Get the property's cached value, or compute and cache it if it
        is not already cached.

        Parameters
        ----------
            instance:
                the instance we are a descriptor for.
            owner:
                the owner type of the instance.
        Returns
        -------
            a coroutine to be awaited to retrieve the cached value.
        """
        return self.__aget(instance, owner)

    async def __aget(self, instance: Any, _: Type) -> T:
        if instance is not None:
            try:
                return getattr(instance, self.__name__)
            except AttributeError:
                val = await self.func(instance)
                setattr(self.func, self.__name__, val)
                return val
        else:
            return self

    def __delete__(self, instance: object):
        """
        Clears the attribute value from the cache, if it exists.

        Parameters
        ----------
            instance:
                the object instance we are a descriptor for.
        """
        try:
            delattr(instance, self.__name__)
        except AttributeError:
            pass
