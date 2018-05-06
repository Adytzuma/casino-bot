import discord
from discord.ext import commands
import asyncio

class Fun:
	def __init__(self, bot):
		self.bot = bot
		self.infections = {}
		#Infections
		"""
		{[user, server.id] : infection_task}
		"""

	@commands.command(pass_context=True, name="infect")
	async def infect_(self, ctx, user: discord.Member = None, emoji = None):
		"""Infects a user with a emoji"""
		if user == None or emoji == None:
			await self.bot.say("Please provide a user and a emoji. Do `c!help infect` for more info")
			return

		def check(msg):
			return ctx.message.server.id == msg.server.id
		
		async def infect(self):
			await self.bot.say("`"user.name + "` has been infected with " + emoji + " for **one** hour")
			
			while True:
				m = await self.bot.wait_for_message(author=user, check =check)
				await self.bot.add_reaction(m, emoji)
		
		in=self.infections.get([user, ctx.message.server.id], None)
		if in != None:
			await self.bot.say("`" + user.name + "` is already infected")
			return

		infection = self.bot.loop.create_task(infect(self))
		self.infections.update([user, ctx.message.server.id] : infection)
		await asyncio.sleep(60 * 60)
		infection.cancel()
		del self.infections[user, ctx.message.server.id]

	@commands.command(pass_context=True)
	async def heal(self, ctx, user: discord.Member = None):
		"""Heals a user from a infection"""
		if user == None:
			await self.bot.say("Please provide a user. Do `c!help heal` for more info")
			return

		if user == ctx.messsage.author:
			await self.bot.say("You can't heal yourself")
			return

		in=self.infections.get([user, ctx.message.server.id], None)
		if in != None:
			in.cancel()
			del self.infections[user, ctx.message.server.id]
			await self.bot.say("`" + user.name + "` has been healed")
		else:
			self.bot.say("`" + user.name +"` was not infected")
			
def setup(bot):
	bot.add_cog(Fun(bot))
