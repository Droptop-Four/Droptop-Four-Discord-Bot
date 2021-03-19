import discord
from discord.ext import commands
import time



class ModCommands(commands.Cog, name='Moderation'):
	'''These are the Mod Commands'''
	


	def __init__(self, bot):
		self.bot = bot	



def setup(bot):
	bot.add_cog(ModCommands(bot))
