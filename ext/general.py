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

	@commands.command(pass_context=True)
	async def invite(self, ctx):
		"""Gives the invite for the official supporter bot server"""
		await self.bot.say("%s, the link for the official supporter bot server is: https://discord.gg/hrN3hmz/" %(ctx.message.author.mention))
	
	@commands.command(pass_context=True)
	async def add(self, ctx):
		"""Sends the invite to add the bot to your server"""
		await self.bot.say("%s, the link to invite the bot is: https://discordapp.com/api/oauth2/authorize?client_id=434057626980974602&permissions=330752&scope=bot" %(ctx.message.author.mention))

	@commands.command(pass_context=True)
	async def feedback(self, ctx, *, message=None):
		"""Sends feedback to the bot developers"""
		if message is None:
			await self.bot.say("Please provide a message. Do `c!help feedback` for more info")	
			return

		await self.bot.send_message(self.bot.get_channel("446296161528315904"), f"**Feedback:**\nUser: {ctx.message.author.mention}\nMessage: {message}")
		await self.bot.say("Your feedback has been sent to the team:thumbsup:")	
def setup(bot):
	bot.add_cog(General(bot))
