#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
The good ol' loggable class mixin to inject named loggers into a class namespace.
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
__all__ = 'Log', 'CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'NOTSET',

import logging
from logging import CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET


class _LoggerProperty:
    """Only generates the logger once we refer to it for the first time."""
    __slots__ = '_logger',

    def __get__(self, instance, owner):
        if not hasattr(self, '_logger'):
            name = owner.__qualname__
            setattr(self, '_logger', logging.getLogger(name))
        return self._logger


class Log:
    log: logging.Logger

    """Class mixin that injects a logger object into the derived class."""
    def __init_subclass__(cls, **kwargs):
        """Init the logger."""
        cls.log: logging.Logger = _LoggerProperty()
