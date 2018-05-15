import discord
from discord.ext import commands
from random import randint

dev_channels = ["416161836069814273", "426699644190326785", "441474231176396800"]

class Poker:
	def __init__ (self, bot):
		self.bot = bot
		self.waiting_games = {}
		self.running_games = []
		self.card_numbers = {"1" : "Ace", "2" : "Two", "3" : "Three", "4" : "Four", "5" : "Five", "6" : "Six", "7" : "Seven", "8" : "Eight", "9" : "Nine", "10" : "Ten", "11" : "Jack", "12" : "Queen", "13" : "King"}
		self.card_symbols = {"1" : "Spades", "2" : "Clubs", "3" : "Hearts", "4" : "Diamonds"}
		self.actions = ["", "", "", "", ""]
		self.msgs = {"choose1" : "**Choose:**\n:spades:\tShows your cards (you will have another action)\n::\tGo in\n::\tRaise bet\n::\tTrash a card\n:x:\tGive up", "choose2", "**Choose:**\n:spades:\tShows your cards (you will have another action)\n::\tGo in\n::\tRaise bet\n:x:\tGive up"}
		
	#Waiting Games Hierarchy
	"""
	{Channel id:[Player1, Player2, Player3, Player4]}
	"""
	
	#Running Games Hierarchy
	"""
	[Channel id]
	"""
	
	def is_testing_channel(ctx):
		if ctx.message.server.id == "415241422736719882" and ctx.message.channel.id in dev_channels:
			return True
		return False
	
	def get_card(self, num):
		#Num1 = Symbol
		#Num2 = Number
		#Eg: 12 = Two of Spades
		#Eg: 35 = Five of Clubs
		
		i = 1
		nm = ""
		for c in num:
			if i == 1:
				sym = self.card_symbols[c]
			else:
				nm = nm + self.card_numbers[c]
			i += 1

		return nm + " of " + sym

	def generate_deck():
		deck = []
		#Generates a empty deck
		for i in range(0, 52):
			deck.append("")

		#Adds cards to the deck in a random order (work in progress)
		symbols = self.card_symbols
		numbers = self.card_numbers
		clubs = []
		spades = []
		hearts = []
		diamonds = []

		for sym in symbols:
			for num in numbers:
				

	async def alert(self, info, user1 = None, user2 = None, user3 = None, user4 = None):
		try:
			await self.bot.send_message(user1, info)
			await self.bot.send_message(user2, info)
			await self.bot.send_message(user3, info)
			await self.bot.send_message(user4, info)
		except:
			pass

	async def start(self, channel_id):
		self.running_games.append(channel_id)
		users = self.waiting_games[channel_id]
		money = [5, 100, 100, 100, 100]
		cards = [self.generate_deck(), "", "", "", ""]
		del self.waiting_games[channel_id]
		
		for i in 
		for rn in range(1, 4):
			for t in range(1, 4):
				if i == 1:
					await self.alert_users(f"{users[0]}\'s turn. Wait for your turn", users[1], users[2], users[3])
				elif i == 2:
					await self.alert_users(f"{users[1]}\'s turn. Wait for your turn", users[0], users[2], users[3])
				elif i == 3:
					await self.alert_users(f"{users[2]}\'s turn. Wait for your turn", users[0], users[1], users[3])
				else:
					await self.alert_users(f"{users[3]}\'s turn. Wait for your turn", users[0], users[1], users[2])
			
				done = False
				while done != True:
					if rn != 1:
						msg = await self.bot.send_message(users[t -1], self.msgs["choose2"]
					else:
						msg = await self.bot.send_message(users[t -1], self.msgs["choose1"])

					with self.actions as a:
						for r in a:
							if r == a[3] and rn != 1:
								pass
							else:
								await self.bot.add_reaction(msg, r)
						if rn == 1:
							rct = await self.bot.wait_for_reaction(message=msg, emoji=a)
						else:
							aa = a
							aa.remove(a[3])
							rct = await self.bot.wait_for_reaction(message=msg, emoji=aa)

						if rtc == a[0]:
							#Show cards
							content = "**Your cards:**\n"
							for c in cards[i]
								card = self.get_card(c)
								content = content + f"\t{card}\n"
							await self.bot.delete_message(msg)
							await self.bot.send_message(users[t -1], content)
							
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
	@commands.command(pass_context=True)
	async def join(self, ctx):
		"""Join a poker game on a channel"""
		channel_id = ctx.message.channel.id
		user= ctx.message.author
		
		if channel_id in self.running_games:
			await self.bot.say('There is already a game running in this channel')
			return
		
		if channel_id in self.waiting_games:
			if user in self.waiting_games[channel_id]:
	        	        await self.bot.say('You are already in the game')
	        	        return
			
			self.waiting_games[channel_id].append(user)
        	
			if len(self.waiting_games[channel_id]) == 4:
				await self.bot.say('Game starting')
				await self.bot.loop.create_task(start(channel_id))
				return
        
			await self.bot.say('<@!%s>, you joined the game, %s players remaining!' %(user.id, 4 - len(self.waiting_games[channel_id])))
			return

		self.waiting_games.update({channel_id:[user]})
		await self.bot.say('<@!%s>, you joined the game, %s players remaining!' %(user.id, 4 - len(self.waiting_games[channel_id])))
			
def setup(bot):
	bot.add_cog(Poker(bot))
