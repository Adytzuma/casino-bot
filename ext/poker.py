from discord.ext import commands
from random import randint
import asyncio

# TODO
# Check for Royal Flush                                              (Not done - Not started)
# Check for Straight flush                                           (Not done - Not started)
# Check for Four of a kind                                           (Not done - Not started)
# Check for Full house                                               (Not done - Not started)
# Check for Flush                                                    (Not done - Not started)
# Check for Straight                                                 (Not done - Not started)
# Check for Three of a kind                                          (Not done - Not started)
# Check for Double pares                                             (Not done - Not started)
# Check for Pair                                                     (Not done - Not started)
# If none is found, then 0 points and name is "Nothing"              (Not done - Not started)
# Replace "\u" with there corresponding unicode character            (Not done - Not started)


dev_channels = [416161836069814273, 426699644190326785, 441474231176396800, 411586546551095296, 339112602867204097]


class Poker():
    def __init__(self, bot):
        self.bot = bot
        self.waiting_games = {}
        self.running_games = []
        self.card_numbers = {
            1: 'Ace',
            2: 'Two',
            3: 'Three',
            4: 'Four',
            5: 'Five',
            6: 'Six',
            7: 'Seven',
            8: 'Eight',
            9: 'Nine',
            10: 'Ten',
            11: 'Jack',
            12: 'Queen',
            13: 'King',
        }
        self.card_symbols = {
            1: 'Spades',
            2: 'Clubs',
            3: 'Hearts',
            4: 'Diamonds',
        }
        self.emojis = {"actions":['\u', '\u', '\u', '\u', '\u'], "numbers_up1":['\u', '\u', '\u', '\u', '\u', '\u', '\u', '\u', '\u', '\u'], "numbers_up2":['\u', '\u', '\u', '\u']}
        self.msgs = {
            'choose1': '**Current money:**\t%s\n**Current bet:**\t%s\n**Availabe actions:**\n::\tShows your cards \
            (you will have another action)\n::\tGo in\n::\tRaise bet\n::\tTrash a card\n:x:\tDrop out',
            'choose2': '**Current money:**\t%s\n**Current bet:**\t%s\n**Availabe actions:**\n::\tShows your cards \
            (you will have another action)\n::\tGo in\n::\tRaise bet\n:x:\tDrop out',
        }

    # Waiting Games Hierarchy
    """{Channel id : [Player1, Player2, Player3, Player4]}"""

    # Running Games Hierarchy
    """[Channel id]"""

    def is_testing_channel(self, ctx):
        if ctx.channel.id in dev_channels:
            return True
        return False

    def get_card(self, num):
        # First number = Symbol
        # Second number = Number
        # Eg: [2, 1] = Two of Spades
        # Eg: [5, 3] = Five of Clubs

        i = 0
        nm = ''
        for c in num:
            if i == 0:
                nm = self.card_numbers[c]
                i = 1
            else:
                sym = self.card_symbols[c]

        return nm + ' of ' + sym

    def generate_deck(self):
        # Generates a empty deck
        deck = []
        for i in range(52):
            deck.append('')

        # Generates a deck with all possible cards
        symbols = self.card_symbols
        numbers = self.card_numbers
        cards = []
        for sym in symbols:
            for num in numbers:
                cards.append([num, sym])

        # Adds the cards to the deck in a random order
        for c in cards:
            card = cards[randint(0, len(cards))]
            deck.append(card)
            cards.remove(card)

    def order(self, cards):
        # Get number of the cards
        cards_numbers = []
        for card in cards:
            cards_numbers.append(card[0])

        # Order the numbers
        ordered_cards_numbers = []
        for n in range(1, 14):
            for c in cards_numbers:
                if c == n:
                    ordered_cards_numbers.append(c)
                    break

        # Order cards
        ordered_cards = []
        for num in ordered_cards_numbers:
            for card in cards:
                if num == card[0]:
                    ordered_cards.append(card)

        return ordered_cards

    async def alert(self, info, users):
        for u in users:
            try:
                await u.send(info)
            except:
                pass

    async def game(self, channel_id):
        self.running_games.append(channel_id)
        users = self.waiting_games[channel_id]
        money = [5, 100, 100, 100, 100]
        cards = [self.generate_deck(), [], [], [], []]
        del self.waiting_games[channel_id]

        # Deal 4 cards per player
        for u in range(1, 5):
            for c in range(1, 6):
                cards[u].append(cards[0][0])
                cards[0].remove(cards[0][0])
        
        for rn in range(1, 5):
            await self.alert("Round {} has started".format(rn), users)

            for t in range(1, len(users) + 1):
                await users[t].send("It's your turn")

                if t == 0:
                    usrs = users
                    usrs.remove(t)

                elif t == 1:
                    usrs = users
                    usrs.remove(t)

                elif t == 2:
                    usrs = users
                    usrs.remove(t)

                else:
                    usrs = users
                    usrs.remove(t)

                await self.alert(users[t].mention + "'s turn. Wait for your turn", usrs)

                done = False
                while done is not True:
                    if rn != 1:
                        msg = await users[t].send(self.msgs['choose2'] %(money[t + 1], money[0]))
                    else:
                        msg = await users[t].send(self.msgs['choose1'] %(money[t + 1], money[0]))

                    with self.emojis["choose"] as a:
                        for r in a:
                            if (r == a[3]) and (rn != 1):
                                pass
                            else:
                                await msg.add_reaction(r)

                        def check(self, reaction, user):
                            return reaction.message == msg

                        try:
                            rtc, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                            rtc = str(rtc.emoji)
                            
                        except asyncio.TimeoutError:
                            # Timeout
                            rtc = '\u'

                        if rtc == a[0]:
                            # Show cards
                            await msg.delete()
                            content = '**Your cards:**\n'
                            for c in cards[t]:
                                card = self.get_card(c)
                                content = content + '\t{}\n'.format(card)

                            await users[t].send(content)

                        elif rtc == a[1]:
                            # Go in
                            await msg.delete()
                            if money[t + 1] < money[0]:
                                await users[t].send("You don't have enough money to go in, please leave the game")
                            else:
                                money[t + 1] = money[t + 1] - money[0]
                                await users[t].send("You went in with {}$".format(money[0]))
                                await self.alert(users[t].mention + " has gone in", usrs)
                                done = True

                        elif rtc == a[2]:
                            # Raise bet
                            await msg.delete()

                            msg = await users[t].send("**Current bet:{}$**\nSelect a number to increment the bet by".format(money[0]))

                            with self.emojis["numbers_up"] as num:
                                for n in num:
                                    msg.add_reaction(n)

                                def check(self, reaction, user):
                                    return reaction.message == msg

                                try:
                                    rtc, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)

                                except asyncio.TimeoutError:
                                    # Timeout
                                    rtc = ''

                                up = 0
                                for i in range(len(num)):
                                    if rtc.emoji == num[i]:
                                        up = i + 1
                                        break

                                if up == 0:
                                    # Invalid emoji
                                    await msg.delete()
                                    await users[t].send("Invalid emoji, try again")

                                else:
                                    # Valid emoji
                                    await msg.delete()
                                    if up + money[0] > money[t + 1]:
                                        await users[t].send("You don't have enough money for do this")
                                    else:
                                        money[0] = money[0] + up
                                        await users[t].send("**You made the bet %s$ bigger.**\nYou went in with {}$".format(money[0]))
                                        await self.alert(users[t].mention + " has increased the bet by {}$".format(up),
                                                         usrs)

                                        done = True

                        elif rtc == a[3] and rn == 1:
                            # Trash a card
                            await msg.delete()
                            content = '**Current cards:**\n'
                            a = 1
                            for c in cards[t]:
                                card = self.get_card(c)
                                content = content + '\t{}. {}\n'.format(a, card)
                                a += 1

                            msg = await users[t].send(content + "Select the number of the card you want to trash".format(money[0]))

                            with self.emojis["numbers_trash"] as num:
                                for n in num:
                                    msg.add_reaction(n)

                                def check(self, reaction, user):
                                    return reaction.message == msg

                                try:
                                    rtc, user= await self.bot.wait_for('reaction_add', timeout=60, check=check)

                                except asyncio.TimeoutError:
                                    # Timeout
                                    rtc = ''

                                cr = None
                                for i in range(len(num)):
                                    if rtc.emoji == num[i]:
                                        cr = i
                                        break

                                if cr is None:
                                    # Invalid emoji
                                    await msg.delete()
                                    await users[t].send("Invalid emoji, try again")

                                else:
                                    # Valid emoji
                                    await msg.delete()

                                    trashed_card = cards[t + 1][cr]
                                    added_card = cards[0][0]

                                    cards[t + 1].remove(trashed_card)
                                    cards[t + 1].append(added_card)
                                    cards[0].remove(added_card)

                                    await users[t].send("You trashed the **{}** and got the **{}**").format(
                                        self.get_card(trashed_card), self.get_card(added_card))
                                    await self.alert(users[t].mention + " trashed a card", usrs)

                                    done = True

                        elif rtc == a[4]:
                            # Drop out
                            await msg.delete()

                            await users[t].send("You dropped out of the game \
                            (you will not be informed about any actions of this game)")
                            await self.alert(users[t].mention + " dropped out of the game", usrs)

                            users.delete(t)
                            done = True

                        else:
                            # Invalid emoji
                            await msg.delete()
                            await users[t].send("Invalid emoji, try again")

            await self.alert("Round {} has concluded".format(rn), users)

        # Game finished
        await self.alert("The game has concluded, the points are going to be counted and the winner will be announced, \
        this will take some time, so **please hold on**", users)
        
        # Calculate points
        # Order cards
        ordered_cards = []
        i = 0
        for card in cards:
            if i == 0:
                i = 1
            else:
                ordered_cards.append(self.order(card))

        # Checks
        # Check for flush

        # Get podium (probably doesnt work)
        podium = [[[], ""], [[], ""], [[], ""], [[], ""]]
#       for point in range(len(points)):
#           pos = 0
#           for p in points:
#               if points[point] < p:
#                   pos += 1
#           podium[pos][0].append(users[point])
#           podium[pos][1] = users_combinations_names[point]

        content = "**Results:**\n"
        a = 1
        for p in podium:
            u = p[0]
            r = p[1]

            if len(u) == 0:
                pass

            elif len(u) == 1:
                content = content + "In position number {} is {} with a {}\n".format(a, u[0].mention, r)
                a += 1

            elif len(u) == 2:
                content = content + "In position number {} are {} and {} with a {}\n".format(a, u[0].mention, u[1].mention, r)
                a += 1

            elif len(u) == 3:
                content = content + "In position number {} are {}, {} and {} with a {}\n".format(a, u[0].mention, u[1].mention, u[2].mention, r)
                a += 1

            else:
                content = content + "In position number {} are {}, {}, {} and {} with a {}\n".format(a, u[0].mention, u[1].mention, u[2].mention, u[3].mention, r)
                a += 1

        await self.alert(content, users)

    @commands.check(is_testing_channel)
    @commands.command(brief='Join a poker game on a channel')
    async def join(self, ctx):
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
            await ctx.send('%s, you joined the game, %s players remaining!' % (user.mention, 4 - len(self.waiting_games[channel_id])))
            return

        self.waiting_games.update({channel_id: [user],})
        await ctx.send('%s, you joined the game, %s players remaining!' % (user.mention, 4 - len(self.waiting_games[channel_id])))


def setup(bot):
    bot.add_cog(Poker(bot))
