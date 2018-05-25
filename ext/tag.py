import discord
from discord.ext import commands


tags=[['tst', 'this is a test'], ['tst2', 'this is another test']]
#Hierarcy
"""[['tag name', 'tag info'], ['other tag name', 'other tag info']]"""

class Tag:
	def __init__(self, bot):
		self.bot = bot

	@commands.group(case_insensitive=True)
	async def tag(self, ctx):
		"""Run help tag for more info"""
		pass
			
	@tag.command(case_insensitive=True)
	async def get(self, ctx, tag=None):
		"""Gets a tag"""
		await ctx.trigger_typing()
		if tag is None:
			return await ctx.send('Please provide a argument. Do `help tag` for more info')
			
		found = None
		for i in tags:
			if i[0] == tag:
				found = i[1]

		if found is None:
			return await ctx.send('Tag not found')

		await ctx.send(found)
		
	@tag.command(case_insensitive=True)
	async def list(self, ctx):
		"""Lists available tags"""
		await ctx.trigger_typing()
		desc = ""
		for i in tags:
			desc = desc + i[0] + "\n"
		
		if desc == "":		
			em = discord.Embed(title='Available tags:', description=None ,colour=discord.Colour(0x00FFFF))
			
		else:
			em = discord.Embed(title='Available tags:', description=desc ,colour=discord.Colour(0x00FFFF))

		await ctx.send(embed=em)
		
	@tag.command(case_insensitive=True)
	async def add(self, ctx, tag_name=None, *, tag_info=None):
		"""Adds a new tag"""
		await ctx.trigger_typing()
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send("You are not allowed to do this")
		
		if tag_name is None or tag_info is None:
			return await ctx.send("Please provide a tag name and the tag info. Do `help tag` for more info")
		
		exists = False
		for i in tags:
			if i[0] == tag_name:
				exists = True
				
		if not exists:
			tags.append([tag_name, tag_info])
			return await ctx.send("The tag has been added")
		
		await ctx.send("The tag already exists")
		
	@tag.command(case_insensitive=True)
	async def remove(self, ctx, tag=None):
		"""Remove a tag"""
		await ctx.trigger_typing()
		if not ctx.author.guild_permissions.manage_guild:
			return await ctx.send("You are not allowed to do this")

		if tag is None:
			return await ctx.send("Please provide a tag name and the tag info. Do `help tag` for more info")
		
		found = None
		for i in tags:
			if i[0] == tag:
				found = i
				
		if found is not None:
			tags.remove(found)
			return await ctx.send("The tag has been removed")
		
		await ctx.send("The tag has not been found")
		
		
def setup(bot):
    bot.add_cog(Tag(bot))
