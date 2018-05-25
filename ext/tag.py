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
	async def tag(self, ctx, tag=None):
		"""Return a tag's content"""
		await ctx.trigger_typing()
		if tag is None:
			return await ctx.send('Please provide a tag name')

		if tag == 'list':
			desc = ""
			for i in tags:
				desc = desc + i[0] + "\n"
				
			em = discord.Embed(title='Available tags:', description=desc ,colour=discord.Colour.blue())

			return await ctx.send(embed=em)

		found = None
		for i in tags:
			if i[0] == tag:
				found = i[1]

		if found is None:
        	    return await ctx.send('No tag found')

		await ctx.send(found)


def setup(bot):
    bot.add_cog(Tag(bot))
