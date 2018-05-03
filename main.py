import discord
from discord.ext import commands

class Main:
	def __init__(self, bot):			
		self.bot = bot
		
	
	async def presence():
		await self.bot.wait_until_ready()
		while not self.bot.is_closed:
			a = 0
			for i in self.bot.servers:
				for u in i.members:
					if u.bot == False:
						a = a+1
			await self.bot.change_presence(game=discord.Game(name=('%s users | %s servers' %(a, len(bot.servers))), type=3))
			await sleep(30)
			await self.bot.change_presence(game=discord.Game(name='c!help', type=2))
			await sleep(30)

	@bot.event
	async def on_ready():
		await ext_reload(bot)
		msg = await self.bot.send_message(await self.bot.get_user_info("377812572784820226"), "Bot deployed :white_check_mark:")
		await sleep(5)
		await self.bot.delete_message(msg)

	@bot.event
	async def on_member_join(member):
		if member.server.id == "415241422736719882":
			if member.bot == True:
				await self.bot.add_roles(member, discord.Object("432826495719833601"))
			else:
				await self.bot.add_roles(member, discord.Object("433607950045544448"))
	@bot.event
	async def on_message(msg):
		if msg.author.bot != True:
			await self.bot.process_commands(msg)

	@bot.event
	async def on_message_edit(before, after):
		if after.author.bot != True:
			await self.bot.process_commands(after)

def setup(bot):
	bot.add_cog(Main(bot))
