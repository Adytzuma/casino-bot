# -*- coding: utf-8 -*-
from discord.ext import commands
from random import randint
import asyncio
from collections import defaultdict
from itertools import combinations

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


dev_channels = [416161836069814273, 426699644190326785, 441474231176396800, 411586546551095296, 339112602867204097]


class Poker:
    def __init__(self, bot):
        self.bot = bot
        self.waiting_games = {}
        self.running_games = []

        self.emojis_str = [None]
        for i in range(1, 11):
            self.emojis_str.append(str(i) + '\N{COMBINING ENCLOSING KEYCAP}')

        self.card_numbers = {
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
            1: 'Ace',
        }

        self.card_symbols = {
            1: 'Hearts',
            2: 'Spades',
            3: 'Diamonds',
            4: 'Clubs',
        }
        self.hands = {
            9:"straight-flush",
            8:"four-of-a-kind",
            7:"full-house",
            6:"flush",
            5:"straight",
            4:"three-of-a-kind",
            3:"two-pairs",
            2:"one-pair",
            1:"highest-card"
        }
        
        self.emojis = {
            "actions1":[self.emojis_str[1], self.emojis_str[2], self.emojis_str[3], self.emojis_str[4], self.emojis_str[5]],
            "actions2":[self.emojis_str[1], self.emojis_str[2], self.emojis_str[3], None , self.emojis_str[4]],
            "numbers_up":[self.emojis_str[1], self.emojis_str[2], self.emojis_str[3], self.emojis_str[4], self.emojis_str[5], self.emojis_str[6], self.emojis_str[7], self.emojis_str[8], self.emojis_str[9], self.emojis_str[10]],
            "numbers_trash":[self.emojis_str[1], self.emojis_str[2], self.emojis_str[3], self.emojis_str[4]]
        }

        self.msgs = {
            'choose1': '**Current money:** %s\n**Current bet:** %s\n**Available actions:**\n1) Shows your cards (you will have another action)\n2) Go in\n3) Raise bet\n4) Trash a card\n5) Drop out',
            'choose2': '**Current money:** %s\n**Current bet:** %s\n**Available actions:**\n1) Shows your cards (you will have another action)\n2) Go in\n3) Raise bet\n4) Drop out',
        }

    # Waiting Games Hierarchy
    """{Channel id : [Player1, Player2, Player3, Player4]}"""

    # Running Games Hierarchy
    """[Channel id]"""

    def is_testing_channel(ctx):
        if ctx.channel.id in dev_channels:
            return True
        return False

    async def alert(self, info, users):
        for u in users:
            try:
                await u.send(info)
            except:
                pass

    def get_card(self, num):
        # First number = Symbol
        # Second number = Number
        # Eg: [2, 1] = Two of Spades
        # Eg: [5, 3] = Five of Clubs

        i = 0
        for c in num:
            if i == 0:
                nm = self.card_numbers[c]
                i = 1
            else:
                sym = self.card_symbols[c]

        return nm + ' of ' + sym

    def generate_deck(self):
        # Generates a deck with all possible cards
        symbols = self.card_symbols
        numbers = self.card_numbers
        cards = []
        for sym in symbols:
            for num in numbers:
                cards.append([num, sym])

        # Adds the cards to the deck in a random order
        deck = []
        for c in cards:
            card = cards[randint(0, len(cards) -1)]
            deck.append(card)
            cards.remove(card)
        
        return deck

    # Checks
    def check_straight_flush(self, hand):
        if self.check_flush(hand) and self.check_straight(hand):
            return True
        else:
            return False

    def check_four_of_a_kind(self, hand):
        values = [i[0] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[v] += 1
        if sorted(value_counts.values()) == [1, 4]:
            return True
        return False

    def check_full_house(self, hand):
        values = [i[0] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[v] += 1
        if sorted(value_counts.values()) == [2, 3]:
            return True
        return False

    def check_flush(self, hand):
        suits = [i[1] for i in hand]
        if len(set(suits)) == 1:
            return True
        else:
            return False

    def check_straight(self, hand):
        values = [i[0] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[v] += 1
        rank_values = [self.card_numbers[i] for i in values]
        value_range = max(rank_values) - min(rank_values)
        if len(set(value_counts.values())) == 1 and (value_range == 4):
            return True
        else:
            # check straight with low Ace
            if set(values) == {1, 2, 3, 4, 5}:
                return True
            return False

    def check_three_of_a_kind(self, hand):
        values = [i[0] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[v] += 1
        if set(value_counts.values()) == {3, 1}:
            return True
        else:
            return False

    def check_two_pairs(self, hand):
        values = [i[0] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[v] += 1
        if sorted(value_counts.values()) == [1, 2, 2]:
            return True
        else:
            return False

    def check_pair(self, hand):
        values = [i[0] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[v] += 1
        if 2 in value_counts.values():
            return True
        else:
            return False


    def check_hand(self, hand):
        if self.check_straight_flush(hand):
            return 9

        if self.check_four_of_a_kind(hand):
            return 8

        if self.check_full_house(hand):
            return 7

        if self.check_flush(hand):
            return 6

        if self.check_straight(hand):
            return 5

        if self.check_three_of_a_kind(hand):
            return 4

        if self.check_two_pairs(hand):
            return 3

        if self.check_pair(hand):
            return 2

        return 1

    def get_play(self, cards):
        hand = cards[:5]
        deck = cards[5:]
        best_hand = 0
        for i in range(6):
            possible_combos = combinations(hand, 5 - i)
            for c in possible_combos:
                current_hand = list(c) + deck[:i]
                hand_value = self.check_hand(current_hand)
                if hand_value > best_hand:
                    best_hand = hand_value

        return [best_hand, self.hands[best_hand]]

    def copy(self, list):
        copied_list = []
        for i in list:
            copied_list.append(i)
        return copied_list

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

            for t in range(0, len(users)):
                await users[t].send("It's your turn")

                usrs = self.copy(users)
                usrs.remove(users[t])

                await self.alert(str(users[t]) + "'s turn. Wait for your turn", usrs)

                done = False
                while done is not True:
                    if rn != 1:
                        msg = await users[t].send(self.msgs['choose2'] %(money[t + 1], money[0]))
                    else:
                        msg = await users[t].send(self.msgs['choose1'] %(money[t + 1], money[0]))
                    
                    if rn == 1:
                        select = 'actions1'
                    else:
                        select = 'actions2'

                    a = self.emojis[select]
                    for r in a:
                        if (r == a[3]) and (rn != 1):
                            pass
                        else:
                            try:
                                await msg.add_reaction(r)
                            except:
                                pass

                    def check(reaction, user):
                        return reaction.message == msg

                    try:
                        rtc, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                        rtc = str(rtc.emoji)
                            
                    except asyncio.TimeoutError:
                        # Timeout
                        rtc = self.emojis_str[5]

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

                            def check(reaction, user):
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
                                    await self.alert(users[t].mention + " has increased the bet by {}$".format(up), usrs)

                                    done = True

                    elif rtc == a[3]:
                        # Trash a card
                        await msg.delete()
                        content = '**Current cards:**\n'
                        b = 1
                        for c in cards[t]:
                            card = self.get_card(c)
                            content = content + '\t{}. {}\n'.format(b, card)
                            b += 1

                        msg = await users[t].send(content + "Select the number of the card you want to trash".format(money[0]))

                        with self.emojis["numbers_trash"] as num:
                            for n in num:
                                msg.add_reaction(n)

                            def check(reaction, user):
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

                        users.remove(t)
                        done = True

                    else:
                        # Invalid emoji
                        await msg.delete()
                        await users[t].send("Invalid emoji, try again")

            await self.alert("Round {} has concluded".format(rn), users)

        # Game finished
        await self.alert("The game has concluded, the points are going to be counted and the winner will be announced, this will take some time, so **please hold on**", users)

        # Order cards
        ordered_cards = []
        i = 0
        for card in cards:
            if i == 0:
                i = 1
            else:
                ordered_cards.append(sorted(card))

        # Get plays
        plays = []
        for hand in ordered_cards:
            plays.append(self.get_play(hand))

        # Get podium
        podium = [[[], ""], [[], ""], [[], ""], [[], ""]]
        for play in range(len(plays)):
            pos = 0
            for p in plays:
                if plays[play] < p:
                    pos += 1
            podium[pos][0].append(users[play + 1])
            podium[pos][1] = plays[play]

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
                await self.game(channel_id)
                return
            await ctx.send('%s, you joined the game, %s players remaining!' % (user.mention, 4 - len(self.waiting_games[channel_id])))
            return

        self.waiting_games.update({channel_id: [user],})
        await ctx.send('%s, you joined the game, %s players remaining!' % (user.mention, 4 - len(self.waiting_games[channel_id])))


def setup(bot):
    bot.add_cog(Poker(bot))
