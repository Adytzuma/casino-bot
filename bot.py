#!/usr/bin/python3
import discord
from discord.ext import commands
from asyncio import sleep
import os

prefixes = {}
def command_prefix_generator (bot, message):
	#Gets costume prefix for server
	if message.channel.name == "no-prefix":
		return ""
	try:
		return [prefixes.get(message.server.id, 'c!'), "<@!434057626980974602> "]
	except AttributeError:
		return ["c!", "<@!434057626980974602> "]

bot = commands.Bot(command_prefix=command_prefix_generator)

bot.load_extension("main")
bot.run(os.getenv('TOKEN'))
