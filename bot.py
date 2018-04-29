#!/usr/bin/python3
import discord
from discord.ext import commands
from asyncio import sleep
from ext.admin import ext_reload
import ext.admin
import os

with open('prefixes.json') as fp:
    PREFIXES = json.load(fp)

def command_prefix_generator (bot, message):
	#Gets costume prefix for server
	try:
		server_id = message.server.id
	except AttributeError:
		return "c!"

	return prefixes.get(server_id, 'c!')

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
		await sleep(60)
		await bot.change_presence(game=discord.Game(name='c!help', type=2))
		await sleep(60)
		
@bot.event
async def on_ready():
	await ext_reload(bot)

@bot.event
async def on_member_jon(member):
	if member.sever.id == "415241422736719882":
		if member.bot == True:
			await bot.add_roles(ctx.message.author, discord.Object("432826495719833601"))
		else:
			await bot.add_roles(ctx.message.author, discord.Object("433607950045544448"))

@bot.event
async def on_message_edit(before, after):
	await bot.process_commands(after)
	
@bot.event
async def on_message(msg):
	if msg.author.bot != True:
		await bot.process_commands(msg)
		
bot.loop.create_task(presence())
bot.run(os.getenv('TOKEN'))
