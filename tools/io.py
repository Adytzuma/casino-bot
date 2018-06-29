#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Useful IO utilities, and general helpers.

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
import copy
import inspect
import logging
import os


def in_this_directory(*path: str, stack_depth: int=0):
    """Refers to a path relative to the caller's file's directory."""
    try:
        frame = inspect.stack()[1 + stack_depth]
    except IndexError:
        raise RuntimeError(
            "Could not find a stack record. Interpreter has " "been shot."
        )
    else:
        module = inspect.getmodule(frame[0])
        assert hasattr(module, "__file__"), "No `__file__' attr, welp."

        # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
        # If Python caches strings rather than copying when we move them
        # around or modify them, then this may cause a referential cycle which
        # will consume more memory and stop the garbage collection system
        # from working correctly. Best thing to do here is deepcopy anything
        # we need and prevent this occuring. Del the references to allow them
        # to be freed.
        file = module.__file__
        file = copy.deepcopy(file)
        del module, frame
        dir_name = os.path.dirname(file)
        abs_dir_name = os.path.abspath(dir_name)
        pathish = os.path.join(abs_dir_name, *path)
        return pathish
