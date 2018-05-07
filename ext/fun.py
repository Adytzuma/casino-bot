import discord
from discord.ext import commands
import asyncio

class Fun:
	def __init__(self, bot):
		self.bot = bot
		self.infections = {}
		#Infections
		"""
		{"user;server.id" : infection_task}
		"""

	@commands.command(pass_context=True, name="infect")
	async def infect_(self, ctx, user: discord.Member = None, emoji = None):
		"""Infects a user"""
		if user == None or emoji == None:
			await self.bot.say("Please provide a user and a emoji. Do `c!help infect` for more info")
			return
		emoji = self.bot.get_emoji(int(emoji.split(":")[2].strip(">"))) if "<:" in emoji or "<a:" in emoji else emoji
		
		def check(msg):
			return ctx.message.server.id == msg.server.id
		
		async def infect(self):
			await self.bot.send_message(ctx.message.channel, "`" + user.name + "` has been infected with " + emoji + " for **one** hour")
			
			while True:
				m = await self.bot.wait_for_message(author=user, check =check)
				await self.bot.add_reaction(m, emoji)
		
		inf=self.infections.get(str(user) + ";" + str(ctx.message.server.id), None)
		if inf != None:
			await self.bot.say("`" + user.name + "` is already infected")
			return

		infection = self.bot.loop.create_task(infect(self))
		self.infections.update({str(user) + ";" + str(ctx.message.server.id) : infection})
		await asyncio.sleep(60 * 60)
		infection.cancel()
		del self.infections[str(user) + ";" + str(ctx.message.server.id)]

	@commands.command(pass_context=True)
	async def heal(self, ctx, user: discord.Member = None):
		"""Heals a user from a infection"""
		if user == None:
			await self.bot.say("Please provide a user. Do `c!help heal` for more info")
			return

		if user == ctx.message.author and ctx.message.author.id != "377812572784820226":
			await self.bot.say("You can't heal yourself")
			return

		inf=self.infections.get(str(user) + ";" + str(ctx.message.server.id), None)
		if inf != None:
			inf.cancel()
			del self.infections[str(user) + ";" + str(ctx.message.server.id)]
			await self.bot.say("`" + user.name + "` has been healed")
		else:
			await self.bot.say("`" + user.name + "` was not infected")
			
def setup(bot):
	bot.add_cog(Fun(bot))
