#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Utilities for string manipulation and voodoo.

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
import re

__all__ = 'join', 'SensitiveStr',


def join(separator: str, iterable, *, cast=str) -> str:
    """
    Join a bunch of items together into a string using the given separator.

    This is the same as str.join, except it casts to string first for you, as
    that kind of makes sense.

    A custom cast method can be provided to override how we obtain the strings.
    By default, it calls the ``str`` builtin. You may wish to change this to
    ``repr`` or something else occasionally.
    """
    iterable = map(cast, iterable)
    return separator.join(iterable)


class SensitiveStr(str):
    """
    Wrapper for sensitive info that blocks the str and repr methods by default.
    To get the underlying string, use the call operator on this object. The reason
    for doing this is to prevent echoing confidential or sensitive data in an
    exec call by accident.
    """
    __slots__ = ()

    # For the json2dataclass implementation.
    __unmarshall__ = True

    def __str__(self) -> str:
        return '<hidden>'

    def __repr__(self) -> str:
        return '<SensitiveStr value=hidden>'

    def __call__(self) -> str:
        return super().__str__()


def cap_start(s: str):
    """Ensures a capital letter at the start, and everywhere else lowercase."""
    return f'{s[0].upper()}{s[1:].lower()}' if s else s


def camelcase_prettify(s: str):
    """delimits """
    return cap_start(" ".join(re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", s)))
