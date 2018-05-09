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

	@commands.command(pass_context=True)
	async def infect(self, ctx, user: discord.Member = None, emoji = None):
		"""Infects a user"""
		if user is None or emoji is None:
			await self.bot.say("Please provide a user and a emoji. Do `c!help infect` for more info")
			return
		
		emoji_stripped= emoji.strip("<>").split(":")[-1][:-1]
		try:							
			int(emoji_stripped)
			emoji = discord.utils.get(self.bot.get_all_emojis(), id=emoji_stripped)
		except Exception as e:
			pass			

		def check(msg):
			return ctx.message.server.id == msg.server.id
		
		async def infect_task(self):
			await self.bot.send_message(ctx.message.channel, "`" + user.name + "` has been infected with " + emoji + " for **one** hour")
			
			while True:
				m = await self.bot.wait_for_message(author=user, check =check)
				await self.bot.add_reaction(m, emoji)
		
		inf=self.infections.get(str(user) + ";" + str(ctx.message.server.id), None)
		if inf != None:
			await self.bot.say("`" + user.name + "` is already infected")
			return
		try:
			await self.bot.add_reaction(ctx.message, emoji)
		except:
			await self.bot.say("Emoji not found")
			
		infection = self.bot.loop.create_task(infect_task(self))
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
