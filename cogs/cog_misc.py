'''
Cog Name: Miscellaneous Commands
Commands: 1
Slash Commands: 0
'''


import discord
from discord.ext import commands
# from discord_slash import SlashCommand, cog_ext, SlashContext
from time import time


class MiscellaneousCommands(commands.Cog, name='Miscellaneous'):
    '''These are the Miscellaneous Commands'''


    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='ping', help='This command returns the latency')
    async def ping(self, ctx):
        '''Returns the latency'''
        
        start = time()
        message = await ctx.send(f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms.')
        end = time()
        await message.edit(content=f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms. The response time is: `{(end-start)*1000:.0f}`ms.')


    # @cog_ext.cog_slash(name="ping", description="Returns the latency")
    # async def slashping(self, ctx: SlashContext):
    #   '''Returns the latency'''
    
    # 	start=time()
    # 	message=await ctx.send(f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms.')
    # 	end=time()
    # 	await message.edit(content=f'**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms. The response time is: `{(end-start)*1000:.0f}`ms.')


def setup(bot):
    bot.add_cog(MiscellaneousCommands(bot))
