import discord
from discord.ext import commands

class Moderation:
	def __init__ (self, bot):
		self.bot = bot		

	@commands.command(pass_context=True)
	async def prefix(self, ctx, new_prefix=None):
		"""Changes the bot prefix"""
		if ctx.message.author.id != '377812572784820226' and ('manage_server', True) not in ctx.message.author.server_permissions:
			await self.bot.say("You are not allowed to perform this action, missing `Manage Server`")
			return	

		old_prefix = self.bot.command_prefix(self.bot, ctx.message)
		if new_prefix == None:
			await self.bot.say("The prefix for this server is \"%s\"" %(old_prefix))		
			return	
		if old_prefix == new_prefix:
			await self.bot.say("Prefix hasn't changed")
			return
		try:
			del prefixes[ctx.message.server.id]
		except KeyError:
			pass
		
		if new_prefix != "c!":
			prefixes.update({ctx.message.server.id: new_prefix})					

		await self.bot.say("Prefix set to \"%s\"" %(new_prefix))
		
def setup(bot):
	bot.add_cog(Moderation(bot))
