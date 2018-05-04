import discord
from discord.ext import commands

class Poker:
	def __init__ (self, bot):
		self.bot = bot
		self.running_games = {}
		self.waiting_games = {}
		
	#Waiting Games Hierarchy
	"""
	{Channel id:[Player1, Player2, Player3, Player4]}
	"""
	
	#Running Games Hierarchy
	"""
	{Channel id:[
		[	
			[Player1, Money, Hand], 
			[Player2, Money, Hand],
			[Player3, Money, Hand], 
			[Player4, Money, Hand]
		]
	]}
	"""
	def start(self, ctx):
		del self.waiting_games[ctx.message.channel.id]
		self.running_games.update({ctx.message.channel.id:[]})
		
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
				self.start(ctx)
				return
        
			await self.bot.say('<@!%s>, you joined the game, %s players remaining!' %(user.id, 4 - len(self.waiting_games[channel_id])))
			return

		self.waiting_games.update({channel_id:[user]})
		await self.bot.say('<@!%s>, you joined the game, %s players remaining!' %(user.id, 4 - len(self.waiting_games[channel_id])))
		

def setup(bot):
	bot.add_cog(Poker(bot))
