import discord
from discord.ext import commands
import asyncio
import typing
import cached_property

from shared import collections, string, fuzzy, commands


class General():
	def __init__(self, bot):
		bot.remove_command('help')
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		'Returns Pong'
		t = await ctx.send('Pong!')
		msg = (t.created_at - ctx.message.created_at).total_seconds() * 1000
		await t.edit(content=':newspaper:Responce time: {}ms\n:cloud:Discord latency: {}ms'.format(int(msg), int(self.bot.latency * 1000)))

	@commands.command()
	async def github(self, ctx):
		'Returns the github URL of the bot'
		await ctx.send('%s, the link for the source code of this bot is: https://github.com/davfsa/casino-bot/' %
					   ctx.author.mention)

	@commands.command()
	async def invite(self, ctx):
		'Gives the invite for the official supporter bot server'
		await ctx.send(
			'%s, the link for the official supporter bot server is: https://discord.gg/aDtBVA4/' % ctx.author.mention)

	@commands.command()
	async def add(self, ctx):
		'Sends the invite to add the bot to your server'
		await ctx.send(
			'%s, the link to invite the bot is: https://discordapp.com/api/oauth2/authorize?client_id=434057626980974602&permissions=330752&scope=bot'
			% ctx.author.mention)

	@commands.command()
	async def feedback(self, ctx, *, message=None):
		'Sends feedback to the bot developers'
		if message is None:
			await ctx.send('Please provide a message. Do `c!help feedback` for more info')
			return
		await self.bot.get_channel(446296161528315904).send((
			('**Feedback:**\nUser: ' + ctx.author.mention) + '\nContent: ') + message)
		await ctx.send('Your feedback has been sent to the team :thumbsup:')

	@commands.command()
	async def bug(self, ctx, *, message=None):
		'Sends a bug report to the bot developers'
		if message is None:
			await ctx.send('Please provide a message. Do `c!help bug` for more info')
			return
		await self.bot.get_channel(446296161528315904).send((
			('**Bug report:**\nUser: ' + ctx.author.mention) + '\nBug: ') + message)
		await ctx.send('Your bug report has been sent to the team :thumbsup:')
		

	@commands.command(brief='Gets usage information for commands.')
	async def help(self, ctx, *, query: str = None):
		"""
		If a command name is given, perform a search for that command and
		display info on how to use it. Otherwise, if nothing is provided, then
		a list of available commands is output instead.

		Provide the `--compact` or `-c` flag to view a compact list of commands
		and aliases to run. This is the original help dialog.
		"""
		if not query:
			await self._new_dialog(ctx)
		elif query.lower() in ('-c', '--compact'):
			await self._summary_screen(ctx, bool(query))
		else:
			result = await self.get_best_match(query, ctx)
			if result:
				# Unpack
				real_match, command = result
				await self._command_page(ctx, query, command, real_match)
			else:
				await ctx.send(f'No command found that matches `{query}`',
							   delete_after=15)

	# noinspection PyUnresolvedReferences
	@staticmethod
	async def _new_dialog(ctx):
		embeds = []
		# Includes those that cannot be run.
		all_cmds = list(sorted(ctx.bot.commands, key=str))

		commands = []

		for potential_command in all_cmds:
			# noinspection PyUnresolvedReferences
			try:
				if await potential_command.can_run(ctx):
					commands.append(potential_command)
			except:
				# E.g. NotOwner is raised.
				continue

		# We only show 10 commands per page.
		for i in range(0, len(commands), 12):
			embed_page = discord.Embed(
				title='Casino commands',
				colour=discord.Colour.grey())
			# embed_page.set_thumbnail(url=ctx.bot.user.avatar_url)

			next_commands = commands[i:i + 12]

			for command in next_commands:
				# Special space char
				name = command.name

				embed_page.add_field(
					name=name,
					# If we put a zero space char first, and follow with an
					# EM QUAD, it won't strip the space.
					value='\u200e\u2001' + (command.brief or '—'),
					inline=False)

			embeds.append(embed_page)

		discomaton.EmbedBooklet(pages=embeds, ctx=ctx).start()

	@staticmethod
	async def _command_page(ctx, query, command, real_match):
		"""
		Replies with info for the given command object.
		:param ctx: the context to reply to.
		:param query: the original query.
		:param command: the command to document.
		:param real_match: true if we had a perfect match, false if we fell
			back to fuzzy.
		"""
		colour = 0x9EE4D9

		pages = []

		def new_page():
			next_page = embeds.Embed(
				title=f'Help for {ctx.bot.command_prefix}'
					  f'{command.qualified_name}',
				colour=colour)
			pages.append(next_page)
			return next_page

		# Generate the first page.
		new_page()

		brief = command.brief
		full_doc = command.help if command.help else ''
		full_doc = string.remove_single_lines(full_doc)
		examples = getattr(command, 'examples', [])
		signature = command.signature
		cog = command.cog_name

		parent = command.full_parent_name
		cooldown = getattr(command, '_buckets')

		if cooldown:
			cooldown = getattr(cooldown, '_cooldown')

		description = [
			f'```markdown\n{ctx.bot.command_prefix}{signature}\n```'
		]

		if cog:
			pages[-1].add_field(
				name='Module defined in',
				value=string.pascal2title(cog))

		if not real_match:
			description.insert(0, f'Closest match for `{query}`')

		if brief:
			description.append(brief)
		pages[-1].description = '\n'.join(description)

		# We detect this later to see if we should start paginating if the
		# description is too long.
		should_paginate_full_doc = False

		if full_doc and len(full_doc) >= 500:
			pages[-1].add_field(
				name='Detailed description',
				value=f'{string.trunc(full_doc, 500)}\n\nContinued on the '
					  'next page...')

			should_paginate_full_doc = True
		elif full_doc:
			pages[-1].add_field(name='Detailed description', value=full_doc)

		if examples:
			examples = '\n'.join(
				f'- `{ctx.bot.command_prefix}{command.qualified_name} '
				f'{ex}`' for ex in examples)
			pages[-1].add_field(name='Examples', value=examples)

		if isinstance(command, commands.BaseGroupMixin):
			_children = sorted(command.commands, key=lambda c: c.name)
			children = []

			for child in _children:
				try:
					if await child.can_run(ctx):
						children.append(child)
				except:
					# This prevents crashing if the child has an is_owner
					# check on it, as dpy raises a NotOwner exception rather
					# than returning False in this case.
					pass
		else:
			children = []

		if children:
			children = ', '.join(f'`{child.name}`' for child in children)
			pages[-1].add_field(name='Child commands', value=children)

		if parent:
			pages[-1].add_field(name='Parent', value=f'`{parent}`')

		if cooldown:
			timeout = cooldown.per
			if timeout.is_integer():
				timeout = int(timeout)

			pages[-1].add_field(
				name='Cooldown policy',
				value=(
					f'{cooldown.type.name.title()}-scoped '
					f'per {cooldown.rate} '
					f'request{"s" if cooldown.rate - 1 else ""} '
					f'with a timeout of {timeout} '
					f'second{"s" if timeout - 1 else ""}'))

		# pages[-1].set_thumbnail(url=ctx.bot.user.avatar_url)

		if hasattr(command.callback, '_probably_broken'):
			pages[0].add_field(name='In active development',
							   value='Expect voodoo-type shit behaviour!')

		if should_paginate_full_doc:
			# Generate pages using the Discord.py paginator.
			pag = discomaton.RapptzPaginator(
				prefix='', suffix='', max_size=1024)

			for line in full_doc.splitlines():
				pag.add_line(line)

			for page in pag.pages:
				next_page = new_page()
				next_page.description = pages[0].description
				next_page.add_field(name='Detailed description',
									value=page)

		if len(pages) == 0:
			raise RuntimeError('Empty help')
		elif len(pages) == 1:
			await ctx.send(embed=pages[-1])
		else:
			# Paginate using embed paginator
			await discomaton.EmbedBooklet(
				pages=pages,
				ctx=ctx).start()

	@staticmethod
	async def _summary_screen(ctx, show_aliases=False):
		"""
		Replies with a list of all commands available.
		:param ctx: the context to reply to.
		"""
		pages = []

		# Get commands this user can run, only.
		async def get_runnable_commands(mixin):
			cmds = []

			for command in mixin.commands:
				# If an error is raised by checking permissions for a command,
				# then just ignore that command.
				try:
					if await command.can_run(ctx):
						cmds.append(command)
				except:
					pass
			return cmds

		current_page = ''

		runnable_commands = await get_runnable_commands(ctx.bot)

		unordered_strings = {}
		for c in runnable_commands:
			if show_aliases:
				for alias in c.aliases:
					unordered_strings[alias] = c
			unordered_strings[c.name] = c

		# Order here now we have the aliases, otherwise the aliases are
		# ignored from the order and it looks kinda dumb.
		keys = list(unordered_strings.keys())
		keys.sort()
		strings = collections.OrderedDict()
		for k in keys:
			strings[k] = unordered_strings[k]

		for i, (name, command) in enumerate(strings.items()):
			if i % 50 == 0 and i < len(strings):
				if current_page:
					current_page += ' _continued..._'
					pages.append(current_page)
					current_page = ''

			if isinstance(command, commands.BaseGroupMixin):
				# This is a command group. Only show if we have at least one
				# available sub-command, though.
				if len(await get_runnable_commands(command)) > 0:
					name = f'{name}...'

			if current_page:
				current_page += ', '
			current_page += f'`{name}`'

		if current_page:
			pages.append(current_page)

		def mk_page(body):
			"""
			Makes a new page with the current body. This is a template
			for embeds to ensure a consistent layout if we can't fit the
			commands list on one page.
			"""
			page = embeds.Embed(
				title='Available Casino Commands',
				colour=0x000663,
				description='The following can be run in this channel:\n\n'
							f'{body}')
			page.set_footer(text='Commands proceeded by ellipses signify '
								 'command groups with sub-commands available.')
			page.add_field(
				name='Want more information?',
				value=f'Run `{ctx.bot.command_prefix}help <command>` '
					  f'for more details on a specific command!',
				inline=False)
			page.set_thumbnail(url=ctx.bot.user.avatar_url)
			return page

		if len(pages) == 0:
			await ctx.send('You cannot run any commands here.')
		elif len(pages) == 1:
			await ctx.send(embed=mk_page(pages.pop()))
		else:
			page_embeds = []
			for page in pages:
				page_embeds.append(mk_page(page))

			fsm = discomaton.EmbedBooklet(pages=page_embeds,
										  ctx=ctx)

			await fsm.start()

	@property
	def all_commands(self) -> typing.FrozenSet[commands.BaseCommand]:
		"""
		Generates a set of all unique commands recursively.
		"""
		return frozenset([command for command in self.bot.walk_commands()])

	@classmethod
	def gen_qual_names(cls, command: commands.Command):
		aliases = [command.name, *command.aliases]

		if command.parent:
			parent_names = [*cls.gen_qual_names(command.parent)]

			for parent_name in parent_names:
				for alias in aliases:
					yield f'{parent_name} {alias}'
		else:
			yield from aliases

	@cached_property
	def alias2command(self) -> typing.Dict:
		"""
		Generates a mapping of all fully qualified command names and aliases
		to their respective command object.
		"""
		mapping = {}

		for command in self.bot.walk_commands():
			for alias in self.gen_qual_names(command):
				mapping[alias] = command
		return mapping

	async def get_best_match(self, string: str, context) \
			-> typing.Optional[typing.Tuple[bool, commands.BaseCommand]]:
		"""
		Attempts to get the best match for the given string. This will
		first attempt to resolve the string directly. If that fails, we will
		instead use fuzzy string matching. If no match above a threshold can
		be made, we give up.

		We take the context in order to only match commands we can actually
		run (permissions).

		The result is a 2-tuple of a boolean and a command. If the output
		is instead None, then nothing was found. The boolean of the tuple is
		true if we have an exact match, or false if it was a fuzzy match.
		"""
		alias2command = self.alias2command

		if string in alias2command:
			command = alias2command[string]
			try:
				if context.author.id == context.bot.owner_id:
					return True, command
				elif await command.can_run(context):
					return True, command
			except:
				pass

		try:
			# Require a minimum of 60% match to qualify. The bot owner
			# gets to see all commands regardless of whether they are
			# accessible or not.
			if context.author.id == context.bot.owner_id:
				result = fuzzy.extract_best(
					string,
					alias2command.keys(),
					scoring_algorithm=fuzzy.deep_ratio,
					min_score=60)

				if not result:
					return None
				else:
					guessed_name, score = result

				return score == 100, alias2command[guessed_name]
			else:
				score_it = fuzzy.extract(
					string,
					alias2command.keys(),
					scoring_algorithm=fuzzy.deep_ratio,
					min_score=60,
					max_results=None)

				for guessed_name, score in score_it:
					can_run = False
					next_command = alias2command[guessed_name]

					try:
						can_run = await next_command.can_run(context)
						can_run = can_run and next_command.enabled
					except:
						# Also means we cannot run
						pass

					if can_run:
						return score == 100, next_command
		except KeyError:
			pass

		return None

		@commands.command(brief='Shows credits')
		async def credits(ctx):
			em = discord.Embed(title="Casino Credits", description=""""Bot creator:<@!377812572784820226>\nSpecial thanks:\nThanks to everyone on the `Sebi Bot Tutorial` server for always helping me out with all of my problems, specially to @Espy and @Dusty.P for always being there to help and sharing code with me that I later used on this bot and @sebi for writing the tutorial that I used to learn how to write the bot.""", colour=discord.Colour.grey())
			await ctx.send(embed=em)
			
def setup(bot):
	bot.add_cog(General(bot))
