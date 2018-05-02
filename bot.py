#!/usr/bin/python3
import discord
from discord.ext import commands
from asyncio import sleep
from ext.admin import ext_reload
import ext.admin
import os

prefixes = {}

def command_prefix_generator (bot, message):
	#Gets costume prefix for server
	if message.channel == "no-prefix":
		return ""
	try:
		return [prefixes.get(message.server.id, 'c!'), "<@!434057626980974602> "]
	except AttributeError:
		return ["c!", "<@!434057626980974602> "]

bot = commands.Bot(command_prefix=command_prefix_generator)

			
async def presence():
	await bot.wait_until_ready()
	while not bot.is_closed:
		a = 0
		for i in bot.servers:
			for u in i.members:
				if u.bot == False:
					a = a+1
		await bot.change_presence(game=discord.Game(name=('%s users | %s servers' %(a, len(bot.servers))), type=3))
		await sleep(30)
		await bot.change_presence(game=discord.Game(name='c!help', type=2))
		await sleep(30)
		
@bot.event
async def on_ready():
	await ext_reload(bot)
	msg = await bot.send_message(await bot.get_user_info(ownerid), "Bot deployed :white_check_mark:")
	await sleep(5)
	await bot.delete_message(msg)
	
@bot.event
async def on_member_join(member):
	if member.server.id == "415241422736719882":
		if member.bot == True:
			await bot.add_roles(member, discord.Object("432826495719833601"))
		else:
			await bot.add_roles(member, discord.Object("433607950045544448"))
@bot.event
async def on_message(msg):
	if msg.author.bot != True:
		await bot.process_commands(msg)
			
@bot.event
async def on_message_edit(before, after):
	if after.author.bot != True:
		await bot.process_commands(after)
		
bot.loop.create_task(presence())
bot.run(os.getenv('TOKEN'))
