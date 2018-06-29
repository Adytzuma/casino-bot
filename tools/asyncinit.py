#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Async factory pattern. Useful if a class needs async methods to be awaited in
the constructor.
"""
__all__ = 'AsyncInit',

import inspect
import typing
import warnings

from . import funcmods


# Set to false to stop updating signatures on initialisation. Reduces accuracy of
# function signatures, but boosts performance.
FIX_TYPES = True


class AsyncInit:
    """
    Base class for a class that needs an asynchronous constructor.

    This modifies some internal signatures to force ``__new__`` to return an
    awaitable with the resultant object inside as the result.

    All implementations should provide an ``__init__`` and an ``__ainit__``
    coroutine function to be called in the respective order on initialisation.

    TODO: add an option to make __init__ non blocking by running in an executor.
    """
    __slots__ = ()

    if FIX_TYPES:
        @classmethod
        def __init_subclass__(cls, **kwargs):
            """Ensures the signatures match and are correct."""
            ainit = getattr(cls, '__ainit__', None)

            if ainit is not None:

                init = cls.__init__
                ainit_sig = inspect.signature(ainit)
                init_sig = inspect.signature(init)

                if ainit_sig != init_sig:
                    raise TypeError(f'__init__ and __ainit__ in {cls.__qualname__} differ by '
                                    f'signature\n\t__init__: {init_sig}\n\t__ainit__: {ainit_sig}')

                if not funcmods.is_coroutine_function(ainit):
                    raise TypeError(f'__ainit__ is not a coroutine function in {cls.__qualname__}')

                new_sig = inspect.signature(init)
                cls_param = inspect.Parameter('cls', inspect.Parameter.POSITIONAL_ONLY)
                # Remove self param.
                params = list(new_sig.parameters.values())[1:]
                params.insert(0, cls_param)
                # Update signature
                new_sig.replace(parameters=params)
                cls.__new__.__signature__ = new_sig
                cls.__anew__.__signature__ = new_sig

            else:
                warnings.warn(f'{cls.__qualname__} implements AsyncInit but lacks an __ainit__ '
                              'constructor.')

            # Ensures all other hooks get called.
            super().__init_subclass__()

    @staticmethod
    def __new__(cls, *args, **kwargs) -> typing.Awaitable:
        # Return a coroutine to be awaited.
        return cls.__anew__(cls, *args, **kwargs)

    @staticmethod
    async def __anew__(cls, *args, **kwargs):
        """Calls both the __init__ and __ainit__ methods."""
        obj = super().__new__(cls)
        cls.__init__(obj, *args, **kwargs)
        if hasattr(cls, '__ainit__'):
            await cls.__ainit__(obj, *args, **kwargs)
        return obj

    if typing.TYPE_CHECKING:
        # Mutes errors caused by the fact we are doing voodoo with __new__
        def __await__(self, *args, **kwargs):
            return self
