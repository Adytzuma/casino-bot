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
from discomaton.factories import bookbinding

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
			
def setup(bot):
	bot.add_cog(Admin(bot))