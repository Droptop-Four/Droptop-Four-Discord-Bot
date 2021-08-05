import discord
from discord.ext import commands
from discord import __version__ as discord_version
from discord_slash import SlashCommand, cog_ext, SlashContext
from time import time
from psutil import Process, virtual_memory
from platform import python_version
from datetime import datetime, timedelta


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


	@cog_ext.cog_slash(name="ping", description="Returns the latency")
	async def slashping(self, ctx: SlashContext):
		start=time()
		message=await ctx.send(f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms.')
		end=time()
		await message.edit(content=f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms. The response time is: `{(end-start)*1000:.0f}`ms.')


	@commands.command(name='infodesk', help='This command returns a welcome message')
	@commands.has_any_role(800217789343727657, 801741190227165236)	#Admin Role ID, Mod Role ID 
	async def infodesk(self, ctx):
		channel = self.bot.get_channel(self.bot.infodeskchannel)
		embed=discord.Embed(title="WELCOME!!", description="Welcome to the Official Droptop Four Discord Server!!", color=0x60d96b)
		embed.set_author(name="Droptop Four", url="https://www.droptopfour.com", icon_url="https://cdn.discordapp.com/icons/800124057923485728/a_4be318be5515b8bcc1bc8f5a68e15e46.webp?size=1024")
		embed.add_field(name="**What is Droptop?**", value="Droptop Four is a popular dropdown app launcher for Windows & Rainmeter. It is available in two version, a `Basic` one, free, and a `Supporter` one, with a 'pay what you want' donation.  Both versions have 14 system tray apps, the Always Show option to make it accessible everywhere on top of your desktop and a lot more.", inline=False)
		embed.add_field(name="**Further Informations**", value="If you have further informations you can use the `-info` command in <#{}>".format(self.bot.botchatchannel), inline=False)
		embed.set_footer(text="If you have other questions, feel free to ask them in the server!")
		await ctx.message.delete()
		await channel.send(embed=embed)


def setup(bot):
	bot.add_cog(InfoCommands(bot))
