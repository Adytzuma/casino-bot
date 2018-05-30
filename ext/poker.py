import discord
from discord.ext import commands
from random import randint
dev_channels = [416161836069814273, 426699644190326785, 441474231176396800]


class Poker():
    def __init__(self, bot):
        self.bot = bot
        self.waiting_games = {}
        self.running_games = []
        self.card_numbers = {
            '1': 'Ace',
            '2': 'Two',
            '3': 'Three',
            '4': 'Four',
            '5': 'Five',
            '6': 'Six',
            '7': 'Seven',
            '8': 'Eight',
            '9': 'Nine',
            '10': 'Ten',
            '11': 'Jack',
            '12': 'Queen',
            '13': 'King',
        }
        self.card_symbols = {
            '1': 'Spades',
            '2': 'Clubs',
            '3': 'Hearts',
            '4': 'Diamonds',
        }
        self.actions = ['', '', '', '', '']
        self.msgs = {
            'choose1': '**Choose:**\n:spades:\tShows your cards (you will have another action)\n::\tGo in\n::\tRaise bet\n::\tTrash a card\n:x:\tGive up',
            'choose2': '**Choose:**\n:spades:\tShows your cards (you will have another action)\n::\tGo in\n::\tRaise bet\n:x:\tGive up',
        }

    #Waiting Games Hierarchy
    """{Channel id:[Player1, Player2, Player3, Player4]}"""
    
    #Running Games Hierarchy
    """[Channel id]"""

    def is_testing_channel(ctx):
        if (ctx.guild.id == 415241422736719882) and (ctx.channel.id in dev_channels):
            return True
        return False

    def get_card(self, num):
		#First number = Symbol
		#Second number = Number
		#Eg: 12 = Two of Spades
		#Eg: 35 = Five of Clubs
		
        i = 1
        nm = ''
        for c in num:
            if i == 1:
                sym = self.card_symbols[c]
            else:
                nm = nm + self.card_numbers[c]
            i += 1
        return (nm + ' of ') + sym

    def generate_deck():
        deck = []
        #Generates a empty deck
        for i in range(0, 52):
            deck.append('')
           
        #Generates a deck with all posible cards
        symbols = self.card_symbols
        numbers = self.card_numbers
        cards = []
        for sym in symbols:
            for num in numbers:
                cards.append(sym + num)
                
        #Adds the cards to the deck in a random order
        for c in cards:
            card = cards[randint(0, len(cards))]
            deck.append(card)
            cards.remove(card)

    async def alert(self, info, user1=None, user2=None, user3=None, user4=None):
        try:
            await user1.send(info)
            await user2.send(info)
            await user3.send(info)
            await user4.send(info)
        except:
            pass

    async def game(self, channel_id):
        self.running_games.append(channel_id)
        users = self.waiting_games[channel_id]
        money = [5, 100, 100, 100, 100]
        cards = [self.generate_deck(), [], [], [], []]
        del self.waiting_games[channel_id]
        
        #Deal 4 cards per player
        for u in range(1, 5):
            for c in range(1, 5):
                cards[u].append(cards[0][0])
                cards[0].remove(cards[0][0])
        
        for rn in range(1, 5):
            for t in range(1, 5):
                if i == 1:
                    await self.alert_users(users[0].mention + "'s turn. Wait for your turn", users[1], users[2],
                                           users[3])
                elif i == 2:
                    await self.alert_users(users[1].mention + "'s turn. Wait for your turn", users[0], users[2],
                                           users[3])
                elif i == 3:
                    await self.alert_users(users[2].mention + "'s turn. Wait for your turn", users[0], users[1],
                                           users[3])
                else:
                    await self.alert_users(users[3].mention + "'s turn. Wait for your turn", users[0], users[1],
                                           users[2])
                done = False
                while done != True:
                    if rn != 1:
                        msg = await users[t - 1].send(self.msgs['choose2'])
                    else:
                        msg = await users[t - 1].send(self.msgs['choose1'])
                    with self.actions as a:
                        for r in a:
                            if (r == a[3]) and (rn != 1):
                                pass
                            else:
                                await msg.add_reaction(r)
                        if rn == 1:
							
                            rct = await self.bot.wait_for('reaction_add')
                        else:
                            
                            aa = a
                            aa.remove(a[3])
                            rct = await self.bot.wait_for('reaction_add')
                            
                        if rtc == a[0]:
							#Show cards
                            content = '**Your cards:**\n'
                            for c in cards[i]:
                                card = self.get_card(c)
                                content = content + '\t{}\n'.format(card)
                            await msg.delete()
                            await users[t - 1].send(content)
                        elif rtc == a[1]:
							#Go in
                            done = True
                        elif rtc == a[2]:
							#Raise bet
                            done = True
                        elif rtc == a[3]:
							#Trash a card
                            done = True 
                        elif rtc == a[4]:
							#Give up
                            done = True


    @commands.check(is_testing_channel)
    @commands.command()
    async def join(self, ctx):  
        'Join a poker game on a channel'
        channel_id = ctx.channel.id
        user = ctx.author
        if channel_id in self.running_games:
            await ctx.send('There is already a game running in this channel')
            return
        if channel_id in self.waiting_games:
            if user in self.waiting_games[channel_id]:
                await ctx.send('You are already in the game')
                return
            self.waiting_games[channel_id].append(user)
            if len(self.waiting_games[channel_id]) == 4:
                await ctx.send('Game starting')
                await self.bot.loop.create_task(game(channel_id))
                return
            await ctx.send('%s, you joined the game, %s players remaining!' % (user.mention,
                                                                               4 - len(self.waiting_games[channel_id])))
            return
        self.waiting_games.update({
            channel_id: [user],
        })
        await ctx.send(
            '%s, you joined the game, %s players remaining!' % (user.mention, 4 - len(self.waiting_games[channel_id])))


def setup(bot):
    bot.add_cog(Poker(bot))
