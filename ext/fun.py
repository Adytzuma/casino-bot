import discord
from discord.ext import commands
import asyncio

class Fun:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def infect(self, ctx, who: discord.Member, what):
	    async def task(ctx):
	        while True:
	            m = await self.bot.wait_for(
	                'message', 
	                check=lambda m: m.author.id == ctx.author.id and m.server.id == ctx.server.id)
	            await m.add_reaction(what)
	    future = self.bot.loop.create_task(task(ctx))
	    await asyncio.sleep(60 * 60)
	    future.cancel()

def setup(bot):
	bot.add_cog(Fun(bot))
