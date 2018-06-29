import discord
from discord.ext import commands

from asyncio import sleep
from os import listdir, getcwd
import traceback
import io
import os
from datetime import datetime
from discomaton.factories import bookbinding

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

bot = commands.Bot(command_prefix='c!')


async def ext_reload(bot):
    # Imports modules
    path = getcwd() + '/ext/'
    files = []
    
    for f in listdir(path):
        if f.endswith('.py'):
            files.append('ext.' + f.replace('.py', ''))
    for i in files:
        try:
            exec('bot.unload_extension("%s")' % i)
            exec('bot.load_extension("%s")' % i)
        except Exception as e:
            stdout = io.StringIO()
            value = stdout.getvalue()
            msg = await bot.get_channel(446291887524020224).send((
                ':warning:**There was a problem while loading the extension `%s`, '
                'please check the error and fix**:warning:'
                % i) + '\nError:```py\n{}{}\n```'.format(value, traceback.format_exc()))
            await msg.add_reaction('❌')


async def presence():
    await bot.wait_until_ready()
    while not bot.is_closed():
        a = 0
        for i in bot.guilds:
            for u in i.members:
                if u.bot is False:
                    a = a + 1

        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='%s users | '
                                                                                                     '%s servers' % 
                                                                                                     (a, len(bot.guilds)
                                                                                                      )))
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
async def on_message(message):
    if message.author.bot is True:
        return
    else:
        await bot.process_commands(message)
    

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.BadArgument):
        return await ctx.send("Invalid user")

    channel = bot.get_channel(446291887524020224)
    await ctx.send("Ups. An unexpected error has been raised, the error has been reported to the developer and will be "
                   "fixed soon :smile:")
    context = (ctx.message, channel, ctx.bot)

    binder = bookbinding.StringBookBinder(context, max_lines=50, prefix='```py', suffix='```', only_author=False)
    
    error = error.__cause__ or error
    fmt = '**`Error in command {}`**\n\n**{}:**'.format(ctx.command, type(error).__name__)
    
    error_string = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    for line in error_string.split('\n'):
        binder.add_line(line)
    
    await channel.send(fmt)
    binder.start()


@bot.event
async def on_guild_join(server):
    em = discord.Embed(title='Server joined', colour=discord.Colour.green(), timestamp=datetime.utcnow())
    em.set_thumbnail(url=server.icon_url)
    em.add_field(name='Server name:', value=server.name, inline=True)
    em.add_field(name='Server id:', value=server.id, inline=True)
    em.add_field(name='Server owner:', value="<@!" + str(server.owner.id) + ">", inline=True)
    await bot.get_channel(446292018415665152).send(embed=em)


@bot.event
async def on_guild_remove(server):
    em = discord.Embed(title='Server left', colour=discord.Colour.gold(), timestamp=datetime.utcnow())
    em.set_thumbnail(url=server.icon_url)
    em.add_field(name='Server name:', value=server.name, inline=True)
    em.add_field(name='Server id:', value=server.id, inline=True)
    em.add_field(name='Server owner:', value="<@!" + str(server.owner.id) + ">", inline=True)
    await bot.get_channel(446292018415665152).send(embed=em)

bot.loop.create_task(presence())
bot.run(os.getenv("TOKEN"))
