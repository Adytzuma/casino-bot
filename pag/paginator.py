#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Paginator implementation.

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
__all__ = 'Paginator',

import collections
from typing import List

from tools import properties

# Marks the intent for a page break.
_PAGE_BREAK = object()

# Marks the intent for a line break.
_LINE_BREAK = object()

# Flags the parser to toggle string truncation.
_DISABLE_TRUNCATION = object()
_ENABLE_TRUNCATION = object()


def _explode_on_any(string) -> List[str]:
    # Ensure each occurrence is only once, but cast to list as that is faster to traverse.
    # Python has faster locals access than globals.
    boundary_chars = [*{
        ' ',
        '\t',
        '\r',
        '\n',
        ', ',
        '; ',
        '. ',
        '-',
        '! ',
        '? ',
        ') ',
        '] ',
        '} '
    }]

    # Linked list makes thousands of allocs less expensive, as it is less likely
    # to require a large block be realloced.
    bits = []

    for c in string:
        if not bits or any(bits[-1].endswith(c) for c in boundary_chars):
            # Start a new buffer.
            bits.append('')
        # Append (gonna be godawful slow)
        bits[-1] += c

    return list(bits)


class Paginator:
    """
    Consumes chunks of string input and formats them neatly into size-bound
    string blocks.

    This operates by caching any chunks to produce from first in a deque. On
    request of either the true object length, or the object pages, we generate
    the chunk of pages formatted according to the configuration. This is stored
    as a cached property for the lifetime of this object, or until the chunk
    queue is altered again.

    This also supports appending to the front, which is rather snazzy, I would
    say.

    Note
    ----
    This has a runtime complexity of

    .. code-block:

                      .oooooo.     .o                   o.
                     d8P'  `Y8b   .8'                   `8.
                    888      888 .8'  ___       __       `8.
                    888      888 88  |__  |  | /  ` |__/  88
                    888      888 88  |    \__/ \__, |  \  88
                    `88b    d88' `8.                     .8'
                     `Y8bood8P'   `8.                   .8'
                                    `"                 `'

    So, just be aware. If you are paginating a large chunk of text, more than
    say 15 pages, you may want to outsource this to an executor. Preferably
    a process pool for faster parallelism.

    I may rewrite this algorithm in C in the future if I can get enough self
    loathing and hatred to attempt it.

    Parameters
    ----------
        max_chars:
            Maximum characters per page. This is an upper limit and must be
            specified.
        max_lines:
            Optional max lines per page. Again, this is an upper limit and is
            not guaranteed to be met. It is guaranteed to not surpass this
            value if specified. If not specified, it is not taken into
            consideration.
        prefix:
            Optional prefix to prepend to each page. Defaults to emptystring.
        suffix:
            Optional suffix to append to each page. Defaults to emptystring.
        line_break:
            Custom line break character. Defaults to \\n LINE FEED
        enable_truncation:
            Default policy for allowing truncation. This defaults to True.
            The policy, if True, allows the paginator to split atomic strings
            that you provide on separation characters (e.g. space, LF, CR,
            tab, and various punctuation characters). If substrings are
            still too large, then we may also split mid-word if necessary. At
            this point, we attempt to get the most compact representation.
            Set this option to False to instead raise an Error, or default to
            moving an atomic string to a new page instead of mutilating it. This
            is useful for pagination of code, or application output, tracebacks,
            et cetera
        TODO: FIX DOCS TO BE CORRECT DESCRIPTION
        force_truncation: if true, as default, we can still split the string
            forcefully midword as a last resort.
    """
    __slots__ = (
        'chunks', '_s_pages', 'max_chars', 'max_lines', 'prefix', 'suffix', 'line_break',
        'force_truncation', '_enable_truncation', '_default_executor'
    )

    def __init__(self,
                 max_chars: int = 2000,
                 max_lines: int = None,
                 prefix: str = '',
                 suffix: str = '',
                 line_break: str = '\n',
                 enable_truncation: bool = True,
                 force_truncation: bool = True) -> None:
        self.chunks = collections.deque()
        self.max_chars = max_chars
        self.max_lines = max_lines

        if prefix and not prefix[-1:].isspace():
            prefix += '\n'
        if suffix and not suffix[-1:].isspace():
            suffix = '\n' + suffix

        self.prefix = prefix
        self.suffix = suffix
        self.line_break = line_break
        self._enable_truncation = enable_truncation
        self._default_executor = None
        self.force_truncation = force_truncation

    def add(self, *objects: object, to_back: bool = True) -> 'Paginator':
        """Add an atomic string to the chunks list."""
        if to_back:
            for obj in objects:
                self.chunks.append(obj)
        else:
            for obj in reversed(objects):
                self.chunks.appendleft(obj)

        return self

    def add_line(self, *objects: object, to_back: bool = True) -> 'Paginator':
        """
        Add a line to the chunks list. This always adds the newline as the
        rightmost element.
        """
        return self.add(*objects, _LINE_BREAK, to_back=to_back)

    def add_page_break(self, *, to_back: bool = True) -> 'Paginator':
        """Requests a page break."""
        to_back and self.chunks.append(_PAGE_BREAK) or self.chunks.appendleft(_PAGE_BREAK)
        return self

    def enable_truncation(self) -> 'Paginator':
        """Enables truncation at the back of the paginator."""
        self.chunks.append(_ENABLE_TRUNCATION)
        return self

    def disable_truncation(self) -> 'Paginator':
        """Disables truncation at the back of the paginator."""
        self.chunks.append(_DISABLE_TRUNCATION)
        return self

    @properties.ReadOnlyProperty
    def truncation(self) -> bool:
        """
        Get the default truncation mode for the object.

        If True, we will initially truncate input if it is too long for one page.
        This first will attempt to split on word separators. If that fails, we
        will split on the best location to produce the fewest pages.
        """
        return self._enable_truncation

    def generate_pages(self) -> List[str]:
        """Alias for returning the ``pages`` property."""
        return self.pages

    @properties.ReadOnlyProperty
    def pages(self) -> List[str]:
        """
        Generates the pages and returns them. This is a potentially computationally
        expensive operation, and will be cached until the paginator is modified again.
        """
        # Here be dragons.

        if not self.chunks:
            return []

        # Our max length is not actually the max length, as we may have a prefix
        # and suffix, also. We need to get their lengths first and offset.
        real_length = self.max_chars - len(self.prefix) - len(self.suffix) - 3

        # Don't expand the first or second generator expressions. This saves memory by
        # not pre-allocating the space.
        chunks = (c is _LINE_BREAK and self.line_break or c for c in self.chunks)

        # Explode all non-critical parts based on the space characters we can escape,
        # using a new lit
        new_chunks = []
        should_truncate = self._enable_truncation
        for chunk in chunks:
            if chunk in (_ENABLE_TRUNCATION, _DISABLE_TRUNCATION):
                should_truncate = chunk is _ENABLE_TRUNCATION
                # We need these again in a moment.
                new_chunks.append(chunk)
            elif chunk is _PAGE_BREAK:
                new_chunks.append(chunk)
            elif should_truncate:
                new_chunks += _explode_on_any(chunk)
            else:
                # Keep the chunked parts as they already are.
                new_chunks.append(chunk)

        chunks = new_chunks
        del new_chunks

        # Paginate
        pages = []

        def page_break():
            """Start a new page."""
            # Remove trailing whitespace
            if pages:
                pages[-1] = str(pages[-1]).rstrip()
            pages.append('')

        def split_force(initial_quota, string):
            """
            Splits a string forcefully on max length. This only really should
            occur as a last resort. Initial quota is used to fill up any
            previous space. Since we are splitting mid-word anyway, we may as
            well compact it.

            Returns an iterator.
            """
            assert initial_quota >= 0

            if initial_quota:
                yield string[:initial_quota]

            for i in range(initial_quota, len(string), real_length):
                yield string[i:i + real_length]

        should_truncate = self._enable_truncation

        while chunks:
            chunk = chunks.pop(0)
            if chunk in (_ENABLE_TRUNCATION, _DISABLE_TRUNCATION):
                # Don't add these
                should_truncate = chunk is _ENABLE_TRUNCATION
            else:

                if not pages:
                    page_break()

                if chunk is _PAGE_BREAK:
                    if str(pages[-1]).strip():
                        # If the current chunk is a break, and the previous was not a break...
                        page_break()

                else:
                    # + 1 to include the first line that does not start with a newline.
                    chunk_nl_count = chunk.count(self.line_break) + 1
                    chunk_char_count = len(chunk)

                    current_nl_count = pages[-1].count(self.line_break)

                    current_char_count = len(pages[-1])

                    char_quota = real_length - current_char_count

                    if chunk_char_count > real_length:
                        if self.force_truncation:
                            # Add the parts to the existing chunk list in the current position.
                            # They can be added on the next iteration. Additionally, we should
                            # pop the current chunk to prevent adding it an infinite number
                            # of times.
                            reversed_parts = [*split_force(char_quota, chunk)]
                            for part in reversed(reversed_parts):
                                chunks.insert(0, part)

                            # Don't page-break, reiterate to process correctly.
                            continue
                        else:
                            raise ValueError(
                                'A chunk is too large to fit into the char limit of '
                                f'{real_length} (not including prefix+suffix) '
                                f'(chunk was {chunk_char_count} in size; '
                                f'{chunk[:60] + "..."!r})'
                            )

                    if self.max_lines and chunk_nl_count > self.max_lines:
                        # We can't solve this one.
                        raise ValueError(
                            'A chunk has too many lines to fit into the line limit of '
                            f'{self.max_lines} (chunk was {chunk_nl_count} lines long; '
                            f'{chunk[:60] + "..."!r})'
                        )

                    if current_char_count + chunk_char_count > real_length:
                        page_break()

                    if self.max_lines and current_nl_count + chunk_nl_count > self.max_lines:
                        page_break()

                    if not pages[-1] and chunk == self.line_break:
                        continue
                    else:
                        pages[-1] += chunk

        del chunks

        actual_pages = []
        for page in pages:
            # No point starting a page with blank lines.
            if page.startswith(self.line_break) and should_truncate:
                page = page[len(self.line_break):]

            actual_pages.append(f'{self.prefix}\n{page}\n{self.suffix}')
        del pages
        return actual_pages

    # Magic methods.
    def __len__(self):
        """
        Gets the actual number of pages. Note this will generate a full cache of the result.
        Use the ``length_hint`` operator for a rough guesstimation that is quick and dirty.
        """
        return len(self.pages)

    def __length_hint__(self):
        """
        Attempt to guess the approximate number of pages that will be produced based on
        char and line counts.
        """

        if self.max_lines and self.max_lines > 0:
            line_counts = sum(str(c).count(self.line_break) for c in self.chunks)
            pages_by_lines = line_counts // line_counts + 1
        else:
            pages_by_lines = 1

        char_counts = sum(len(str(c)) for c in self.chunks)
        pages_by_chars = char_counts // self.max_chars + 1

        return max(pages_by_chars, pages_by_lines)

    def __iadd__(self, other: object) -> 'Paginator':
        """Adds one element to the back."""
        self.add(other)
        return self

    def __invert__(self):
        """Reverses the chunk ordering in-place."""
        self.chunks.reverse()

    def __reversed__(self):
        """Creates a reversed view of the chunks internally."""
        return reversed(self.chunks)

    @classmethod
    def set_default_executor(cls, executor):
        """Overwrite the default executor for all instances of the paginator."""
        cls._default_executor = executor
