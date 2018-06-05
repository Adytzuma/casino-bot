import discord
from discord.ext import commands
import asyncio
import typing
from cached_property import cached_property
import discomaton
from shared import collections, string, fuzzy, commands


class General():
	def __init__(self, bot):
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

	@commands.command(brief='Shows credits')
	async def credits(self, ctx):
		em = discord.Embed(title="Casino Credits", description=""""Bot creator: <@!377812572784820226>\nSpecial thanks:\nThanks to everyone on the `Sebi Bot Tutorial` server for always helping me out with all of my problems, specially to <@!351794468870946827> and <@!387871282756190208> for always being there to help and sharing code with me that I later used on this bot and <@!242887101018931200> for writing the tutorial that I used to learn how to write the bot.""", colour=discord.Colour.light_grey())
		await ctx.send(embed=em)
			
def setup(bot):
	bot.add_cog(General(bot))
