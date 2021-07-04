import discord
from discord.ext import commands
from time import time



class InfoCommands(commands.Cog, name='Info'):
	'''These are the Info Commands'''
	


	def __init__(self, bot):
		self.bot = bot



	@commands.command(name='ping', help='This command returns the latency')
	async def ping(self, ctx):
		start=time()
		message=await ctx.send(f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms.')
		end=time()
		await message.edit(content=f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms. The response time is: `{(end-start)*1000:.0f}`ms.')
	


def setup(bot):
	bot.add_cog(InfoCommands(bot))
