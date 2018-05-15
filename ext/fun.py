import discord
from discord.ext import commands
import asyncio
import aiohttp, os, traceback
from PIL import Image

class Fun:
	def __init__(self, bot):
		self.bot = bot
		self.infections = {}
		#Infections
		"""
		{"user;server.id" : infection_task}
		"""

	@commands.command(pass_context=True)
	async def infect(self, ctx, user: discord.Member = None, emoji = None):
		"""Infects a user"""
		if user is None or emoji is None:
			await self.bot.say("Please provide a user and a emoji. Do `c!help infect` for more info")
			return
		
		emoji_stripped= emoji.strip("<>").split(":")[-1]
		try:							
			int(emoji_stripped)
			emoji = discord.utils.get(self.bot.get_all_emojis(), id=emoji_stripped)
		except Exception as e:
			pass			

		def check(msg):
			return ctx.message.server.id == msg.server.id
		
		async def infect_task(self):
			await self.bot.send_message(ctx.message.channel, "`" + user.name + "` has been infected with " + str(emoji) + " for **one** hour")
			
			while True:
				m = await self.bot.wait_for_message(author=user, check =check)
				try:
					await self.bot.add_reaction(m, emoji)
				except:
					pass
		
		
		inf=self.infections.get(str(user) + ";" + str(ctx.message.server.id), None)
		if inf is not None:
			await self.bot.say("`" + user.name + "` is already infected")
			return
		try:
			await self.bot.add_reaction(ctx.message, emoji)
		except:
			await self.bot.say("Emoji not found")
			return
			
			
		infection = self.bot.loop.create_task(infect_task(self))
		self.infections.update({str(user) + ";" + str(ctx.message.server.id) : infection})
		await asyncio.sleep(60 * 60)
		infection.cancel()
		del self.infections[str(user) + ";" + str(ctx.message.server.id)]

	@commands.command(pass_context=True)
	async def heal(self, ctx, user: discord.Member = None):
		"""Heals a user from a infection"""
		if user is None:
			await self.bot.say("Please provide a user. Do `c!help heal` for more info")
			return

		if user == ctx.message.author and ctx.message.author.id != "377812572784820226":
			await self.bot.say("You can't heal yourself")
			return

		inf=self.infections.get(str(user) + ";" + str(ctx.message.server.id), None)
		if inf is not None:
			inf.cancel()
			del self.infections[str(user) + ";" + str(ctx.message.server.id)]
			await self.bot.say("`" + user.name + "` has been healed")
		else:
			await self.bot.say("`" + user.name + "` was not infected")
	
	@commands.command(pass_context=True)
	async def fist(self, ctx, user: discord.Member = None):
		"""Fists a user"""
		if user is None:
			user = ctx.message.author
		edits = 4
		spaces = 12
		time_to_wait = 0.4
		msg = await self.bot.say(f"{user.mention}" + "\t"*int(edits*spaces) + ":left_facing_fist:")
		for i in range(edits):
			edits -= 1
			await asyncio.sleep(time_to_wait)
			await self.bot.edit_message(msg, f"{user.mention}" + "\t"*int(edits*spaces) + ":left_facing_fist:")
			if edits == 0:
				await self.bot.edit_message(msg, f":boom: <----- This is you {user.mention}")

	@commands.command(pass_context=True)
	async def blurpify(self, ctx, user:discord.Member = None):
		"""Makes the users profile picture blurple"""
		user = user or ctx.message.author
		async with aiohttp.ClientSession() as cs:
			async with cs.get(user.avatar_url) as r:
				with open("temp.png", "wb") as f:
					f.write(await r.read())

		im = Image.open("temp.png")
		im = im.resize((256, 256))
		im = im.convert("RGB")
		px = im.load()
		for x in range(0, im.size[0]):
			for y in range(0, im.size[1]):
				r, g, b = px[x, y]
				if (r+g+b)/3>180:
					px[x, y] = (114, 137, 218)
				else:
					px[x, y] = (225, 225, 225)
		im.save("temp.jpg")
		await self.bot.upload("temp.jpg")
		os.remove("temp.jpg")

		
def setup(bot):
	bot.add_cog(Fun(bot))
