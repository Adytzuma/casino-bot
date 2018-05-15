import discord
from discord.ext import commands
from asyncio import sleep
from os import listdir, getcwd
from os.path import isfile, join
import traceback
from contextlib import redirect_stdout
import io
import os

def command_prefix_generator (bot, message):
	#Gets costume prefix for server
	if message.channel.name == "no-prefix":
		return ""
	return "c!"

bot = commands.Bot(command_prefix=command_prefix_generator)

async def await_reaction(bot, msg):
	await bot.wait_for_reaction(emoji="\u274C", message=msg, user=(await bot.get_user_info(ownerid)))
	await bot.delete_message(msg)

async def ext_reload(bot):
	#Imports modules
	path = getcwd() + "/ext/"
	files = []
	for f in listdir(path):
		if f.endswith('.py'):
			files.append('ext.' + f.replace(".py", ""))
		
	msgs = []
	for i in files:
		try:		
			exec("bot.unload_extension(\"%s\")" %(i))
			exec ("bot.load_extension(\"%s\")" %(i))
		except Exception as e:
			stdout = io.StringIO()
			value = stdout.getvalue()
			msg = await bot.send_message(await bot.get_user_info(ownerid), ":warning:**There was a problem while loading the extension `%s`, please check the error and fix**:warning:" %(i) + '\nError:```py\n{}{}\n```'.format(value, traceback.format_exc()))
			await bot.add_reaction(msg, "\u274C")
			msgs.append(msg)
			
	if msgs != []:
		for i in range(0, len(msgs)):
			bot.loop.create_task(await_reaction(bot, msgs[i]))

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
	msg = await bot.send_message(await bot.get_user_info("377812572784820226"), "Bot deployed :white_check_mark:")
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
