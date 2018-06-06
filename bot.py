import discord
from discord.ext import commands
from asyncio import sleep
from os import listdir, getcwd
from os.path import isfile, join
import traceback
from contextlib import redirect_stdout
import io
import os
from datetime import datetime

bot = commands.Bot(command_prefix='c!')


async def ext_reload(bot):
    #Imports modules
    path = getcwd() + '/ext/'
    files = []
	
    for f in listdir(path):
        if f.endswith('.py'):
            files.append('ext.' + f.replace('.py', ''))
    msgs = []
    for i in files:
        try:
            exec('bot.unload_extension("%s")' % i)
            exec('bot.load_extension("%s")' % i)
        except Exception as e:
            stdout = io.StringIO()
            value = stdout.getvalue()
            msg = await bot.get_channel(446291887524020224).send((
                ':warning:**There was a problem while loading the extension `%s`, please check the error and fix**:warning:'
                % i) + '\nError:```py\n{}{}\n```'.format(value, traceback.format_exc()))
            await msg.add_reaction('❌')


async def presence():
    await bot.wait_until_ready()
    while not bot.is_closed():
        a = 0
        for i in bot.guilds:
            for u in i.members:
                if u.bot == False:
                    a = a + 1

        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='%s users | %s servers' % (a, len(bot.guilds))))
        await sleep(30)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='c!help'))
        await sleep(30)


@bot.event
async def on_ready():
    await ext_reload(bot)
    em = discord.Embed(title='Bot deployed', colour=discord.Colour.green(), timestamp=datetime.utcnow())
    msg = await bot.get_channel(446298417413750786).send(embed=em)
    await msg.add_reaction('✅')
	
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
		return
	if isinstance(error, commands.commands.errors.BadArgument):
		return await ctx.send("Invalid user")
	await ctx.send("Ups. An unexpected error has been raised, the error has been reported to the developers and will be fixed soon :smile:")
	error = error.__cause__ or error
	tb = traceback.format_exception(type(error), error, error.__traceback__, limit=2, chain=False)
	tb = ''.join(tb)
	fmt = '**`Error in command {}`**\n\n**{}:**\n```py\n{}\n```'.format(ctx.command, type(error).__name__, tb)
	await bot.get_channel(446291887524020224).send(fmt) 


@bot.event
async def on_guild_join(guild):
    em = discord.Embed(title='Server joined', colour=discord.Colour.green(), timestamp=datetime.utcnow())
    em.set_image(url=server.icon_url)
    em.add_field(name='Server name:', value=server.name)
    em.add_field(name='Server id:', value=server.id)
    em.add_field(name='Server owner:', value=server.owner.mention)
    await bot.get_channel(446292018415665152).send(embed=em)


@bot.event
async def on_guild_remove(guild):
    em = discord.Embed(title='Server left', colour=discord.Colour.gold(), timestamp=datetime.utcnow())
    em.set_image(url=server.icon_url)
    em.add_field(name='Server name:', value=server.name)
    em.add_field(name='Server id:', value=server.id)
    em.add_field(name='Server owner:', value=server.owner.mention)
    await bot.get_channel(446292018415665152).send(embed=em)


bot.loop.create_task(presence())
bot.run(os.getenv("TOKEN"))
