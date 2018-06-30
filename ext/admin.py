# -*- coding: utf-8 -*-
"""
Exec command for calling stuff in either the current interpreter or shell. This
also contains the logic to restart the bot.

A panic subcommand is provided to quickly eject this cog. The bot would then
require an alternative way of restarting and exec'ing arbitrary code until it
restarts or has the cog reloaded.
"""
import asyncio
import contextlib
import io
import pprint
import re
import shutil
import sys
import time
import traceback

import discord
from discord.ext import commands

from libneko.pag import factory

sudo = [377812572784820226]

class Admin:
    """
    Owner-only hidden exec command.
    """
    async def has_perm(ctx):
        return ctx.author.id in sudo

    
    @commands.check(has_perm)
    @commands.group(name='sudo', invoke_without_command=True)
    async def sudo_group(self, ctx):
        pass

    @sudo_group.command(name='exec', aliases=['shell'])
    async def execute(self, ctx, *, code):
        """Executes the given code."""

        # Removes code blocks if they are present. This then captures the
        # syntax highlighting to use if it is present.
        code_block = re.findall(r"```([a-zA-Z0-9]*)\s([\s\S(^\\`{3})]*?)\s*```", code)

        if code_block:
            lang, code = code_block[0][0], code_block[0][1]

            if lang == 'py':
                lang = 'python'
        else:
            lang = 'python' if ctx.invoked_with == 'exec' else 'bash'

        executor = self.execute_in_session if lang is 'python' else self.execute_in_shell

        async with ctx.typing():
            sout, serr, result, exec_time, prog = await executor(ctx, lang, code)

        # Todo: use my pag.
        pag = factory.StringNavigatorFactory(
            prefix='```markdown\n',
            suffix='```',
            max_lines=25,
            enable_truncation=False
        )

        nl = '\n'
        pag.add_line(f'# Using {prog.replace(nl, " ")}')

        if sout:
            pag.add_line('# stdout:')
            for line in sout.split('\n'):
                pag.add_line(line)
        if serr:
            pag.add_line('# stderr:')
            for line in serr.split('\n'):
                pag.add_line(line)
        if len(str(result)) > 100:
            pag.add_line(f'# Took approx {1000 * exec_time:,.2f}ms; returned:')
            for p in pprint.pformat(result, indent=4).split('\n'):
                pag.add_line(p)
        else:
            pag.add_line(f'# Returned {result} in approx {1000 * exec_time:,.2f}ms.')

        await pag.start(ctx)

    async def execute_in_session(self, ctx, _program, code):
        """Executes the code in the current interpreter session."""
        sout = io.StringIO()
        serr = io.StringIO()

        # Intrinsics to eval the line where possible if it is one line.
        # This will implicitly cause the result of await expressions to be
        # awaited, which is cool.
        if code.count('\n') == 0:
            brackets = ('(', ')'), ('[', ']'), ('{', '}')

            def count_check(c1, c2):
                return code.count(c1) == code.count(c2)

            # If matched brackets
            if all(count_check(c1, c2) for c1, c2 in brackets):
                stripped = code.lstrip()
                if not any(stripped.startswith(x) for x in ('raise', 'return ', 'yield ')):
                    code = 'return ' + stripped

        # Redirect all streams.
        with contextlib.redirect_stdout(sout):
            with contextlib.redirect_stderr(serr):
                nl = '\n'
                func = (
                    'async def aexec(ctx, bot):\n'
                    f'{nl.join(" " * 4 + line for line in code.split(nl))}'
                )

                start_time = time.monotonic()
                # noinspection PyBroadException
                try:
                    exec(func)
                    result = await locals()['aexec'](ctx, ctx.bot)
                except BaseException as ex:
                    traceback.print_exc()
                    result = type(ex)
                finally:
                    exec_time = time.monotonic() - start_time

        return sout.getvalue(), serr.getvalue(), result, exec_time, sys.version

    async def execute_in_shell(self, _ctx, program, code):
        """Executes the given program in-shell."""
        path = shutil.which(program)
        if not path:
            return '', f'{program} not found.', 127, 0.0

        start_time = time.monotonic()
        process = await asyncio.create_subprocess_exec(
            path, '--',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE
        )

        sout, serr = await process.communicate(bytes(code, 'utf-8'))
        exec_time = time.monotonic() - start_time

        exit_code = process.returncode

        sout = sout.decode()
        serr = serr.decode()

        return sout, serr, str(exit_code), exec_time, path

    @sudo_group.command()
    async def logout(self, ctx):
        """Makes the bot log out."""
        await ctx.message.add_reaction('\N{OK HAND SIGN}')
        await ctx.bot.logout()

def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(Admin())
