#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Pagination and large-text navigation utilities for Neko3.

Components:
    - ``button.py`` - contains a datatype for representing a reaction on a message
        as a clickable button. Also contains several example button objects you can
        use for common tasks.
    - ``paginator.py`` - contains a class that consumes text in chunks and
        tries to the best of it's ability to format the content in a desirable and
        clean layout that fits within the given line count and character count
        constraints. TL;DR - lots of text is input, and it outputs chunks of
        text that are less than 2000 characters in size so that they fit in
        messages.
    - ``navigator.py`` - a state machine that handles displaying buttons on a
        message, and transitioning between pages created by a paginator.
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
