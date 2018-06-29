#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import typing


T = typing.TypeVar('T')


def find(condition: typing.Callable[[T], bool], iterable: typing.Iterable[T]) -> typing.Optional[T]:
    try:
        return next(filter(condition, iterable))
    except StopIteration:
        return None
