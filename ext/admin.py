from discord.ext import commands
import discord
import contextlib
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
import async_timeout

# MIT License
#
# Copyright (c) 2018 Davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

global admin_perm_id
admin_perm_id = [377812572784820226]


class Admin():
	def __init__(self, bot):
		self.bot = bot

	def is_owner(ctx):
		if ctx.author.id in admin_perm_id:
			return True
		return False
	
	def cleanup_code(self, content):
		'Automatically removes code blocks from the code.'
		if content.startswith('```') and content.endswith('```'):  # remove ```py\n```
			return '\n'.join(content.split('\n')[1:(-1)])
		return content 

	@commands.check(is_owner)
	@commands.command() 
	async def exec(self, ctx, *, command):
		'Execute or evaluate code in python'
		binder = bookbinding.StringBookBinder(ctx, max_lines=50,prefix='```py', suffix='```')
		command = self.cleanup_code(command)
		
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
												  for line in command.split('\n')) +
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
