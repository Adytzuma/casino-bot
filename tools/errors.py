#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Utilities and helpers for Exception handling.

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
__all__ = 'ExceptionT', 'TripletT', 'get_triplet', 'unwrap_cause',

from typing import Generic, NoReturn, Type, TypeVar, Union

# Get the underlying type implementation for a traceback.
try:
    raise Exception
except Exception as _exc:
    TracebackT = type(_exc.__traceback__)
    del _exc

ExceptionT = TypeVar('ExceptionT', bound=BaseException)


class TripletT(Generic[ExceptionT]):
    """Wraps an Exception or a triplet of type, value and traceback."""
    __slots__ = '_value',

    def __init__(self,
                 exc_type: Union[ExceptionT, Type[ExceptionT]],
                 value: ExceptionT = None,
                 traceback: TracebackT = None) -> None:

        if value is None and traceback is None:
            exc_type, value, traceback = type(exc_type), exc_type, exc_type.__traceback__

        self._value = [exc_type, value, traceback]

    def __getitem__(self, item):
        return self._value[item]

    def __len__(self):
        return len(self._value)

    @property
    def type(self) -> Type[ExceptionT]:
        """Returns the type of exception."""
        return self[0]

    @property
    def value(self) -> ExceptionT:
        """Returns the exception."""
        return self[1]

    @property
    def traceback(self) -> TracebackT:
        """Returns the traceback."""
        return self[2]

    def __call__(self, **kwargs) -> NoReturn:
        """
        Reraises this error.

        Parameters:
            context: optional context to raise from.
        """
        has_ctx = 'context' in kwargs
        if has_ctx:
            raise self.value from kwargs['context']
        else:
            raise self.value


def get_triplet(ex: ExceptionT) -> (Type[ExceptionT], ExceptionT, TracebackT):
    """Gets the python exception triplet (e_type, e, tb) from an exception."""
    return TripletT(type(ex), ex, ex.__traceback__)


def unwrap_cause(ex: ExceptionT) -> ExceptionT:
    """
    If the exception passed has a cause, we return that cause. Otherwise we
    return the input exception.
    """
    return getattr(ex, '__cause__', None) or ex

