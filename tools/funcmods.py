#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Function modifications, decorators and utilities.

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
__all__ = (
    'is_generator_coroutine_function', 'is_generator_coroutine', 'is_coroutine_function',
    'is_coroutine', 'is_async_def_coroutine', 'is_async_def_function', 'steal_signature_from',
    'wraps'
)

import asyncio
import functools
import inspect
import typing


# True for both old-style and new-style coroutines (generators and async-defs)
is_coroutine_function = asyncio.iscoroutinefunction
is_coroutine = asyncio.iscoroutine

is_async_def_function = inspect.iscoroutinefunction
is_async_def_coroutine = inspect.iscoroutine


def is_generator_coroutine_function(what):
    """Returns True if this is a generator coroutine function, not an async def."""
    return not is_async_def_function(what) and is_coroutine_function(what)


def is_generator_coroutine(what):
    """Returns True if this is a generator coroutine, but not an async def one."""
    return not is_async_def_coroutine(what) and is_coroutine(what)


def ensure_coroutine_function(func):
    """
    Ensures the given argument is awaitable. If it is not, then we wrap it in a
    coroutine function and return that.
    """
    if is_coroutine_function(func):
        return func
    else:
        @wraps(func)
        async def coroutine_fn(*args, **kwargs):
            """Wraps the function in a coroutine."""
            return func(*args, **kwargs)

        return coroutine_fn


def steal_signature_from(original_func):
    """
    Makes a decorator that will replace original_func with the decorated argument.

    The decorated argument will have the same apparent signature as the initial
    function, which is useful for defining decorators, etc.
    """

    def decorator(new_func):
        """Decorates the function with the original_func signature."""
        # Update the signature
        orig_sig = inspect.signature(original_func)
        setattr(new_func, '__signature__', orig_sig)
        return new_func

    return decorator


def wraps(original_func):
    """
    Similar to the implementation of functools.wraps, except this preserves the
    asynchronous traits of a function where applicable.

    Produces a decorator to decorate a replacement function with.

    References
    ----------
        https://www.python.org/dev/peps/pep-0362/#visualizing-callable-objects-signature

    """

    def decorator(new_func):
        """
        Replaces the decorated function with a signature closer to that of
        what was passed to ``wraps``.
        """

        # Ensures coroutine-ness
        if asyncio.iscoroutinefunction(original_func) and not asyncio.iscoroutinefunction(new_func):
            raise TypeError('Cannot replace an async-def with a def')

        return steal_signature_from(original_func)(functools.wraps(original_func)(new_func))

    return decorator


def print_result(func):
    if is_async_def_function:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            print(f'coro {func}', *args, kwargs, '->', result)
            return result
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(f'func {func}', *args, kwargs, '->', result)
            return result

    return wrapper