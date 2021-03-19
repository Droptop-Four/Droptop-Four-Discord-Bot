import discord
from discord.ext import commands
import time



class HelpCommands(commands.Cog, name='Help'):
	'''These are the Info Commands'''
	


	def __init__(self, bot):
		self.bot = bot



	@commands.command(name='help', help='This command returns the latency')
	async def ping(self, ctx):
		# await ctx.send("pong!")
		await ctx.send("This command will be used for Droptop Four support, but right now it isn't ready yet.\nTo see all the commands that you can use right now you should use `-bothelp`.")
	
	

def setup(bot):
	bot.add_cog(HelpCommands(bot))
