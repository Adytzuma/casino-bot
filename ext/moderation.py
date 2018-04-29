import discord
from discord.ext import commands
import json

class Moderation:
	def __init__ (self, bot):
		self.bot = bot
	
	@commands.command(pass_context=True)
	async def prefix(self, ctx, new_prefix="c!"):
		"""Change the bot prefix"""
		if ctx.message.author.id != '377812572784820226' and ('manage_server', True) not in ctx.message.author.server_permissions:
			await self.bot.say("You are not allowed to perform this action, missing `Manage Server`")
			return
			
		old_prefix = self.bot.command_prefix(self.bot, ctx.message)
		if old_prefix == new_prefix:
			await self.bot.say("Prefix hasnt't changed, prefix is \"%s\"" %(old_prefix))
			return
			
		with open("prefixs.json") as f:
			try:
				prefixs = json.load(f)
			except:
				prefixs = {}
			
		try:
			del prefixs[ctx.message.server.id]
		except KeyError:
			pass
		
		if new_prefix != "c!":
			prefixs.update({ctx.message.server.id: new_prefix})
		
		with open("prefixs.json", "w") as f:
			f.write(json.dumps(prefixs, indent=4 * ' '))

			
		await self.bot.say("Prefix set to \"%s\"" %(new_prefix))
		
def setup(bot):
	bot.add_cog(Moderation(bot))
