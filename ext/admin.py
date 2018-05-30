from discord.ext import commands
from contextlib import redirect_stdout
import discord
import traceback
import io
import time
import datetime
import math
import asyncio
import inspect
import textwrap

global admin_perm_id
admin_perm_id = [377812572784820226]


class Admin():
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def is_owner(ctx):
        if ctx.author.id in admin_perm_id:
            return True
        return False

    def cleanup_code(self, content):
        'Automatically removes code blocks from the code.'
        if content.startswith('```') and content.endswith('```'):  # remove ```py\n```
            return '\n'.join(content.split('\n')[1:(-1)])
        return content.strip('> \n')

    def get_syntax_error(self, e):  # remove `foo`
        if e.text is None:
            return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    @commands.check(is_owner)
    @commands.command(name='exec')
    async def _eval(self, ctx, *, body: str):
        'Execute or evaluate code in python'
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'server': ctx.guild,
            'msg': ctx.message,
            '_': self._last_result,
        }
        env.update(globals())
        body = self.cleanup_code(body)
        stdout = io.StringIO()
        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')
        try:
            exec(to_compile, env)
        except SyntaxError as e:
            await ctx.send(self.get_syntax_error(e))
            try:
                await ctx.message.add_reaction('⚠')
            except:
                pass
            return
        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send('```py\n{}{}\n```'.format(value, traceback.format_exc()))
            await ctx.message.add_reaction('⚠')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('✅')
            except:
                pass
            if ret is None:
                if value:
                    await ctx.send('```py\n%s\n```' % value)
            else:
                self._last_result = ret
                await ctx.send('```py\n%s%s\n```' % (value, ret))

    @commands.check(is_owner)
    @commands.command()
    async def repl(self, ctx):
        'Starts a repl session'
        msg = ctx.message
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'msg': msg,
            'server': msg.guild,
            'channel': msg.channel,
            'author': msg.author,
            '_': None,
        }
        if msg.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return
        self.sessions.add(msg.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')
        
        def check(msg):
            return msg.content.startswith('>')) and msg.author.id in admin_perm_id
        
        while True:
            _error = False
            response = await self.bot.wait_for('message', check=check)
            cleaned = self.cleanup_code(response.content)
            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(msg.channel.id)
                return
            executor = exec
            if cleaned.count('\n') == 0:
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval
            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    try:
                        await response.add_reaction('⚠')
                    except:
                        pass
                    _error = True
                    continue
            variables['msg'] = response
            fmt = None
            stdout = io.StringIO()
            try:
                with redirect_stdout(stdout):  # single statement, potentially 'eval'
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = '```py\n{}{}\n```'.format(value, traceback.format_exc())
                try:
                    await response.add_reaction('⚠')
                except:
                    pass
                _error = True
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = '```py\n{}{}\n```'.format(value, result)
                    variables['_'] = result
                elif value:
                    fmt = '```py\n{}\n```'.format(value)
            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await msg.channel.send('Content too big to be printed.')
                    else:
                        await msg.channel.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await msg.channel.send('Unexpected error: `{}`'.format(e))
                try:
                    await response.add_reaction('⚠')
                except:
                    pass
                _error = True
            if _error != True:
                try:
                    await response.add_reaction('✅')
                except:
                    pass


def setup(bot):
    bot.add_cog(Admin(bot))