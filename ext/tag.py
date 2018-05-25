"""
=== 

MIT License

Copyright (c) 2018 Dusty.P https://github.com/dustinpianalto

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""


import discord
from discord.ext import commands


tags=[['tst', 'this is a test'], ['tst2', 'this is another test']]
#Hierarcy
"""[['tag name', 'tag info'], ['other tag name', 'other tag info']]"""

class Tag:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(case_insensitive=True)
	async def tag(self, ctx, *, arg=None):
		"""Return a tag's content"""
		await ctx.trigger_typing()
		if arg is None:
			return await ctx.send('Please provide a argument. Do `help tag` for more info')

		if arg == 'list':
			desc = ""
			for i in tags:
				desc = desc + i[0] + "\n"
				
			em = discord.Embed(title='Available tags:', description=desc ,colour=discord.Colour(0x00FFFF))

			return await ctx.send(embed=em)
			
		found = None
		for i in tags:
			if i[0] == tag:
				found = i[1]

		if found is None:
			return await ctx.send('Tag not found')

		await ctx.send(found)
		
	@commands.command(case_insensitive=True)
	async def tadd(self, ctx, tag_name=None, *, tag_info=None):
		"""Adds a tag"""
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
		
	@commands.command(case_insensitive=True)
	async def tremove(self, ctx, tag=None):
		"""Removes a tag"""
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
			tags.remove(i)
			return await ctx.send("The tag has been removed")
		
		await ctx.send("The tag has not been found")
def setup(bot):
    bot.add_cog(Tag(bot))
