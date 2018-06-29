#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Collection type extensions and custom data structures.

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
import typing


ValueT = typing.TypeVar('ValueT')


class Proxy(typing.Generic[ValueT]):
    """
    A defaultdict-like object that allows dot-notation for access. Returns None
    if not present. This can take a dict object positionally, or a group of
    key-value pairs as keyword arguments.
    """
    def __init__(self, from_dict=None, **kwargs) -> None:
        if from_dict is not None:
            self.__dict__.update(**from_dict)
        self.__dict__.update(**kwargs)

    def __getitem__(self, key: str) -> ValueT:
        if key.startswith('__'):
            raise NameError('Cannot modify internals.')
        return self.__dict__.__getitem__(key)

    # Reference: https://docs.python.org/3.6/library/collections.html#collections.defaultdict
    def __missing__(self, key: str) -> ValueT:
        return self.__dict__.setdefault(key, None)

    def __setitem__(self, key: str, value: ValueT):
        if key.startswith('__'):
            raise NameError('Cannot modify internals.')
        return self.__dict__.__setitem__(key, value)

    def __delitem__(self, key: str) -> None:
        if key.startswith('__'):
            raise NameError('Cannot modify internals.')
        return self.__dict__.__delitem__(key)

    # noinspection PyShadowingNames
    def __filtered(self):
        return tuple(key for key in self.__dict__ if not key.startswith('__'))

    def keys(self):
        return self.__filtered()

    def values(self):
        return tuple(v for k, v in self.items())

    def items(self):
        return {k: self[k] for k in self.keys()}

    def __str__(self) -> str:
        return str(self.__filtered())

    def __repr__(self) -> str:
        return repr(self.__filtered())

    def __len__(self) -> int:
        return sum(True for key in self.__dict__ if not key.startswith('__'))

    def __contains__(self, item: str) -> bool:
        return item in self.__filtered()

    def __iter__(self):
        return self.__filtered()

    def __getattr__(self, item) -> typing.Optional:
        return self.__dict__.get(item, None)

    __setattr__ = __setitem__
    __delattr__ = __delitem__
