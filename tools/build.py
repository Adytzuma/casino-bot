#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Automated version numbers.

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
__all__ = 'get_build', 'get_year_string', 'get_most_recent_commit',

import datetime
import os
import shutil
import subprocess


def get_build():
    """Get the build count and total commit count."""
    # current_build:
    #     The commit number for this specific branch/major version.
    # total_build:
    #     The overall commit number for the entire project.
    current_build, total_build = None, None

    if '.git' in os.listdir(os.getcwd()) and shutil.which('git'):
        current_build = subprocess.check_output(
            'git log --pretty=format:"."', universal_newlines=True, shell=True)
        total_build = subprocess.check_output(
            'git log --all --pretty=format:"."', universal_newlines=True, shell=True)

        current_build = str(current_build.count('\n'))
        total_build = str(total_build.count('\n'))

    return current_build, total_build


def get_year_string():
    """Get the string timespan for the project copyright."""
    year = datetime.datetime.now().year
    if year <= 2018:
        return '2018'
    else:
        return f'2018-{year}'


def get_most_recent_commit():
    """Attempts to query the most recent commit, using Git."""
    if shutil.which('git'):
        first, _, second = subprocess.check_output(
            "git log --pretty='format:`#%h`%n`%ar` %B' -n 1",
            universal_newlines=True,
            shell=True
        ).rstrip().partition('\n')

        return first, second
    else:
        return '', 'Unavailable'
