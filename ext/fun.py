import discord
from discord.ext import commands
import asyncio
import aiohttp, os, traceback
from PIL import Image


class Fun():
    def __init__(self, bot):
        self.bot = bot
        self.infections = {  #Infections
        }
        '\n\t\t{"user;server.id" : infection_task}\n\t\t'

    @commands.command()
    async def infect(self, ctx, user: discord.Member = None, emoji=None):
        'Infects a user'
        if (user is None) or (emoji is None):
            await ctx.send('Please provide a user and a emoji. Do `c!help infect` for more info')
            return
        emoji_stripped = emoji.strip('<>').split(':')[(-1)]
        try:
            int(emoji_stripped)
            emoji = discord.utils.get(self.bot.emojis, id=emoji_stripped)
        except Exception as e:
            pass

        def check(msg):
            return ctx.guild.id == msg.guild.id and msg.author.id == user.id

        async def infect_task(self):
            await ctx.channel.send(((
                ('`' + user.name) + '` has been infected with ') + str(emoji)) + ' for **one** hour')
            while True:
                m = await self.bot.wait_for('message', check=check)
                try:
                    await m.add_reaction(emoji)
                except:
                    pass

        inf = self.infections.get((str(user) + ';') + str(ctx.guild.id), None)
        if inf is not None:
            await ctx.send(('`' + user.name) + '` is already infected')
            return
        try:
            await ctx.message.add_reaction(emoji)
        except:
            await ctx.send('Emoji not found')
            return
        infection = self.bot.loop.create_task(infect_task(self))
        self.infections.update({
            (str(user) + ';') + str(ctx.guild.id): infection,
        })
        await asyncio.sleep(60 * 60)
        infection.cancel()
        del self.infections[(str(user) + ';') + str(ctx.guild.id)]

    @commands.command()
    async def heal(self, ctx, user: discord.Member = None):
        'Heals a user from a infection'
        if user is None:
            await ctx.send('Please provide a user. Do `c!help heal` for more info')
            return
        if (user == ctx.author) and (ctx.author.id != 377812572784820226):
            await ctx.send("You can't heal yourself")
            return
        inf = self.infections.get((str(user) + ';') + str(ctx.guild.id), None)
        if inf is not None:
            inf.cancel()
            del self.infections[(str(user) + ';') + str(ctx.guild.id)]
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
                await msg.edit(content=':boom: <----- This is you' + user.mention)

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
