import discord
from discord.ext import commands
import asyncio

class General:
	def __init__ (self, bot):
		self.bot = bot
		
	@commands.command(pass_context=True)
	async def ping(self, ctx):
		"""Returns Pong"""
		t = await self.bot.say('Pong!')
		ms = (t.timestamp-ctx.message.timestamp).total_seconds() * 1000
		await self.bot.edit_message(t, new_content='Ping time: {}ms'.format(int(ms)))
		
	@commands.command(pass_context=True)
	async def github(self, ctx):
		"""Returns the github URL of the bot"""
		await self.bot.say("%s, the link for the source code of this bot is: https://github.com/davfsa/casino-bot/" %(ctx.message.author.mention))


def setup(bot):
	bot.add_cog(General(bot))
