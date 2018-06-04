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
		binder = bookbinding.StringBookBinder(ctx, max_lines=50,
											  prefix='```python',
											  suffix='```')

		try:
			binder.add_line('# Output:')
			if command.count('\n') == 0:
				with async_timeout.timeout(10):
					if command.startswith('await '):
						command = command[6:]
					result = eval(command)
					if inspect.isawaitable(result):
						binder.add_line(
							f'# automatically awaiting result {result}')
						result = await result
					binder.add(str(result))
			else:
				with async_timeout.timeout(60):
					with io.StringIO() as output_stream:
						with contextlib.redirect_stdout(output_stream):
							with contextlib.redirect_stderr(output_stream):
								wrapped_command = (
										'async def _aexec(ctx):\n' +
										'\n'.join(f'	{line}'
												  for line
												  in command.split('\n')) +
										'\n')
								exec(wrapped_command)
								result = await (locals()['_aexec'](ctx))
						binder.add(output_stream.getvalue())
						binder.add('# Returned ' + str(result))
		except:
			binder.add(traceback.format_exc())
		finally:
			binder.start()


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
			return msg.content.startswith('>') and msg.author.id in admin_perm_id
		
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