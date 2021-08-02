import discord
from discord.ext import commands
import time


class PollsCommands(commands.Cog, name='Polls'):
	'''These are the Polls Commands'''


	def __init__(self, bot):
		self.bot = bot


	@commands.command(name='poll', help='This command creates a poll')
	@commands.has_any_role(800217789343727657, 801741190227165236)	#Admin Role ID, Mod Role ID 
	async def poll(self, ctx, emoji1, emoji2):
		'''Use -poll <emoji1> <emoji2>'''
		def check(message):
			return message.author == ctx.author and message.channel == ctx.channel
		pollping = discord.utils.get(ctx.guild.roles, id=self.bot.pollping)
		titlereq = await ctx.send('Waiting for a title')
		title = await self.bot.wait_for('message', check=check)
		descreq = await ctx.send('Waiting for a description')
		desc = await self.bot.wait_for('message', check=check)
		embed = discord.Embed(title=title.content, description=desc.content, color=discord.Color.from_rgb(75, 215, 100))
		embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
		await ctx.send(f'New poll for you! {pollping.mention}')
		embedsend = await ctx.send(embed=embed)
		await embedsend.add_reaction(emoji1)
		await embedsend.add_reaction(emoji2)
		await ctx.message.delete()
		await titlereq.delete()
		await title.delete()
		await descreq.delete()
		await desc.delete()
	

	@poll.error
	async def _poll_error(self, ctx, error):
		if isinstance (error, commands.MissingRequiredArgument):
			embed = discord.Embed(title='Syntax Error', color=0xFF2E00)
			embed.add_field(name='{}poll command'.format(self.bot.command_prefix), value='{}poll <emoji1> <emoji2>'.format(self.bot.command_prefix), inline=False)
			embsend=await ctx.send(embed=embed)
			time.sleep(5)
			await ctx.message.delete()
			time.sleep(15)
			await embsend.delete()


def setup(bot):
	bot.add_cog(PollsCommands(bot))
