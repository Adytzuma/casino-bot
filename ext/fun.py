import discord
from discord.ext import commands
import asyncio
import aiohttp, os, traceback
from PIL import Image
import time

# MIT License
#
# Copyright (c) 2018 Davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class Fun():
	def __init__(self, bot):
		self.bot = bot
		self.infections = {  #Infections
		}
		"""{"user;server.id" : infection_task}"""

	@commands.command()
	async def infect(self, ctx, user: discord.Member = None, emoji=None):
		'Infects a user'
		if (user is None) or (emoji is None):
			return await ctx.send('Please provide a user and a emoji. Do `c!help infect` for more info')
			
		emoji = self.bot.get_emoji(int(emoji.split(':')[2].strip('>'))) if '<:' in emoji or '<a:' in emoji else emoji 

		def check(msg):
			return ctx.guild.id == msg.guild.id and msg.author.id == user.id

		async def infect_task(self):
			await ctx.channel.send(((('`' + user.name) + '` has been infected with ') + str(emoji)) + ' for **one** hour')
			start = time.monotonic()
			while time.monotonic() - start < (60*60):
				m = await self.bot.wait_for('message', check=check)
				try:
					await m.add_reaction(emoji)
				except (discord.Forbidden, discord.HTTPException, discord.NotFound, discord.InvalidArgument):
					pass
			del self.infections[str(user.id) + ';' + str(ctx.guild.id)]

		inf = self.infections.get((str(user.id) + ';') + str(ctx.guild.id), None)
		if inf is not None:
			return await ctx.send(('`' + user.name) + '` is already infected')
			
		try:
			await ctx.message.add_reaction(emoji)
		except:
			return await ctx.send('Emoji not found')
			
		infection = self.bot.loop.create_task(infect_task(self))
		self.infections.update({str(user.id) + ';' + str(ctx.guild.id): infection})

	@commands.command()
	async def heal(self, ctx, user: discord.Member = None):
		'Heals a user from a infection'
		if user is None:
			await ctx.send('Please provide a user. Do `c!help heal` for more info')
			return
		if (user == ctx.author) and (ctx.author.id != 377812572784820226):
			await ctx.send("You can't heal yourself")
			return
		inf = self.infections.get((str(user.id) + ';') + str(ctx.guild.id), None)
		if inf is not None:
			inf.cancel()
			del self.infections[str(user.id) + ';' + str(ctx.guild.id)]
			await ctx.send(('`' + user.name) + '` has been healed')
		else:
			await ctx.send(('`' + user.name) + '` was not infected')

	@commands.command()
	async def fist(self, ctx, user: discord.Member = None):
		'Fists a user'
		if user is None:
			user = ctx.author
		edits = 4
		spaces = 12
		time_to_wait = 0.4
		msg = await ctx.send((user.mention + ('\t' * int(edits * spaces))) + ':left_facing_fist:')
		for i in range(edits):
			edits -= 1
			await asyncio.sleep(time_to_wait)
			await msg.edit(content=(user.mention + ('\t' * int(edits * spaces))) + ':left_facing_fist:')
			if edits == 0:
				await msg.edit(content=':boom: <----- This is you ' + user.mention)

	@commands.command()
	async def blurpify(self, ctx, user: discord.Member = None):
		'Makes the users profile picture blurple'
		user = user or ctx.author
		async with aiohttp.ClientSession() as cs:
			async with cs.get(user.avatar_url) as r:
				with open('temp.png', 'wb') as f:
					f.write(await r.read())
		im = Image.open('temp.png')
		im = im.resize((256, 256))
		im = im.convert('RGB')
		px = im.load()
		for x in range(0, im.size[0]):
			for y in range(0, im.size[1]):
				(r, g, b) = px[(x, y)]
				if (((r + g) + b) / 3) > 180:
					px[(x, y)] = (114, 137, 218)
				else:
					px[(x, y)] = (225, 225, 225)
		im.save('temp.jpg')
		await ctx.send(file=discord.File('temp.jpg'))
		os.remove('temp.jpg')


def setup(bot):
	bot.add_cog(Fun(bot))
