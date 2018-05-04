import discord
from discord.ext import commands
import asyncio

class Fun:
	def __init__(self, bot):
		self.bot = bot
	@commands.command()
	async def infect(self, who: discord.Member, what: discord.Emoji):
	    async def task():
	        while True:
	            m = await self.bot.wait_for(
	                'message', 
	                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id)
	            await m.add_reaction(what)
	    future = self.bot.loop.create_task(task())
	    await asyncio.sleep(60 * 60)
	    future.cancel()

def setup(bot):
	bot.add_cog(Fun(bot))
