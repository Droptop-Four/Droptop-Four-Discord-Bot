import discord
from discord.ext import commands
import time



class InfoCommands(commands.Cog, name='Info'):
	'''These are the Info Commands'''
	


	def __init__(self, bot):
		self.bot = bot



	@commands.command(name='ping', help='This command returns the latency')
	async def ping(self, ctx):
		# await ctx.send("pong!")
		await ctx.send(f'**Pong!** The latency is: {round(self.bot.latency * 1000)}ms')
	
	

def setup(bot):
	bot.add_cog(InfoCommands(bot))
