import discord
from discord.ext import commands

class General:
	def __init__ (self, bot):
		self.bot = bot
		
	@commands.command(pass_context=True)
	async def ping(self, ctx):
		"""Returns Pong"""
		t = await self.bot.say('Pong!')
		ms = (t.timestamp-ctx.message.timestamp).total_seconds() * 1000
#		lat = ctx.bot.latency * 1000
		await self.bot.edit_message(t, new_content='Ping time: {}ms'.format(int(ms)))
		
def setup(bot):
	bot.add_cog(General(bot))
