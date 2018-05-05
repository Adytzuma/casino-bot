import discord
from discord.ext import commands
import asyncio

class Fun:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True, name="infect")
	async def infect_(self, ctx, who: discord.Member, what):

		def check(msg):
			return ctx.message.server.id == msg.server.id
		
		def infect(self):
			await self.bot.say(who.name + " has been infected with " + what + "for **one hour**")
			while True:
				m = await self.bot.wait_for_message(author=who, check =check)
				await self.bot.add_reaction(m, what)
		
		infection = self.bot.loop.create_task(infect())
		await asyncio.sleep(60 * 60)
		infection.cancel()

def setup(bot):
	bot.add_cog(Fun(bot))
