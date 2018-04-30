from discord.ext import commands
from os import listdir, getcwd
from os.path import isfile, join
from contextlib import redirect_stdout
import discord
import json
import traceback
import io
import time
import datetime
import math
import asyncio
import inspect
import textwrap

ownerid = "377812572784820226"
async def await_reaction(msg):
	await bot.wait_for_reaction(emoji="\u274C", message=msg, user=(await bot.get_user_info(ownerid)))
	await bot.delete_message(msg)

async def ext_reload(bot):
	#Imports modules
	path = getcwd() + "/ext/"
	files = []
	for f in listdir(path):
		if f.endswith('.py'):
			files.append('ext.' + f.replace(".py", ""))
		
	msgs = []
	for i in files:
		try:		
			exec("bot.unload_extension(%s)" %(i))
			exec ("bot.load_extension(%s)" %(i))
		except Exception as e:
			stdout = io.StringIO()
			value = stdout.getvalue()
			msg = await bot.send_message(await bot.get_user_info(ownerid), ":warning:**There was a problem while loading the extension `%s`, please check the error and fix**:warning:" %(i) + '\nError:```py\n{}{}\n```'.format(value, traceback.format_exc()))
			await bot.add_reaction(msg, "\u274C")
			msgs.append(msg)
			
	if msgs != []:
		for i in range(0, len(msgs)):
			bot.loop.create_task(await_reaction(msgs[i]))
		
class Admin:
	def __init__(self, bot):
		self.bot = bot
		self._last_result = None
		self.sessions = set()
	
	def is_owner(ctx):
		if ctx.message.author.id == ownerid:
			return True
		return False
		
	def cleanup_code(self, content):
		"""Automatically removes code blocks from the code."""
		# remove ```py\n```
		if content.startswith('```') and content.endswith('```'):
			return '\n'.join(content.split('\n')[1:-1])
 
		# remove `foo`
		return content.strip('> \n')
 
	def get_syntax_error(self, e):
		if e.text is None:
			return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
		return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)
 
	@commands.check(is_owner)
	@commands.command(pass_context=True, name='exec')
	async def _eval(self, ctx, *, body: str):
		"""Execute or evaluate code in python"""
		
		env = {
			'bot': self.bot,
			'ctx': ctx,
			'channel': ctx.message.channel,
			'author': ctx.message.author,
			'server': ctx.message.server,
			'msg': ctx.message,
			'_': self._last_result
		}
 
		env.update(globals())
 
		body = self.cleanup_code(body)
		stdout = io.StringIO()
 
		to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')
 
		try:
			exec(to_compile, env)
		except SyntaxError as e:
			await self.bot.say(self.get_syntax_error(e))
			await self.bot.add_reaction(ctx.message, '\u26A0')
			return
 
		func = env['func']
		try:
			with redirect_stdout(stdout):
				ret = await func()
		except Exception as e:
			value = stdout.getvalue()
			await self.bot.say('```py\n{}{}\n```'.format(value, traceback.format_exc()))
			await self.bot.add_reaction(ctx.message, '\u26A0')
		else:
			value = stdout.getvalue()
			try:
				await self.bot.add_reaction(ctx.message, '\u2705')
			except:
				pass
 
			if ret is None:
				if value:
					await self.bot.say('```py\n%s\n```' % value)
			else:
				self._last_result = ret
				await self.bot.say('```py\n%s%s\n```' % (value, ret))
 
	@commands.check(is_owner)
	@commands.command(pass_context=True)
	async def repl(self, ctx):
		"""Starts a repl session"""
		
		msg = ctx.message
 
		variables = {
			'ctx': ctx,
			'bot': self.bot,
			'msg': msg,
			'server': msg.server,
			'channel': msg.channel,
			'author': msg.author,
			'_': None,
		}
		 
		if msg.channel.id in self.sessions:
			await self.bot.say('Already running a REPL session in this channel. Exit it with `quit`.')
			return
			 
		self.sessions.add(msg.channel.id)
		await self.bot.say('Enter code to execute or evaluate. `exit()` or `quit` to exit.')
		while True:
			_error = False
			response = await self.bot.wait_for_message(author=msg.author, channel=msg.channel,
														check=lambda m: m.content.startswith('>'))
 
			cleaned = self.cleanup_code(response.content)
 
			if cleaned in ('quit', 'exit', 'exit()'):
				await self.bot.say('Exiting.')
				self.sessions.remove(msg.channel.id)
				return
 
			executor = exec
			if cleaned.count('\n') == 0:
				# single statement, potentially 'eval'
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
					await self.bot.say(self.get_syntax_error(e))
					await self.bot.add_reaction(response, '\u26A0')
					_error = True
					continue
 
			variables['msg'] = response
 
			fmt = None
			stdout = io.StringIO()
 
			try:
				with redirect_stdout(stdout):
					result = executor(code, variables)
					if inspect.isawaitable(result):
						result = await result
			except Exception as e:
				value = stdout.getvalue()
				fmt = '```py\n{}{}\n```'.format(value, traceback.format_exc())
				await self.bot.add_reaction(response, '\u26A0')
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
						await self.bot.send_message(msg.channel, 'Content too big to be printed.')
					else:
						await self.bot.send_message(msg.channel, fmt)
			except discord.Forbidden:
				pass
			except discord.HTTPException as e:
				await self.bot.send_message(msg.channel, 'Unexpected error: `{}`'.format(e))
				await self.bot.add_reaction(response, '\u26A0')
				_error = True
			
			if _error != True:
				try:
					await self.bot.add_reaction(response, '\u2705')
				except:
					pass

def setup(bot):
	bot.add_cog(Admin(bot))
