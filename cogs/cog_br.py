'''
Cog Name: Broadcast Commands
Commands: 3
Slash Commands:0
'''


import discord
from discord.ext import commands
import os
import time


class BroadcastCommands(commands.Cog, name='Broadcast'):
    '''These are the Broadcast Commands'''


    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='brdt', help='This command creates a Droptop Announcement', aliases=['broadcast-droptop', 'droptopbr', 'droptopbroadcast', 'droptop-broadcast'])
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def brdt_embed(self, ctx):
        '''Creates a Droptop Announcement'''

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        dtbrping = discord.utils.get(ctx.guild.roles, id=self.bot.droptopping)  # Droptop BR role ID
        channel = self.bot.get_channel(self.bot.annchannel)  # Droptop Announcements channel ID

        titlereq = await ctx.send('Waiting for a title')
        title = await self.bot.wait_for('message', check=check)

        descreq = await ctx.send('Waiting for a description')
        desc = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title=title.content, description=desc.content, color=discord.Color.from_rgb(75, 215, 100))
        embed.set_author(name="Droptop News", url=self.bot.dtsite, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        await channel.send(f'New Droptop Announcement! {dtbrping.mention}')
        embedsend = await channel.send(embed=embed)

        await ctx.message.delete()
        await titlereq.delete()
        await title.delete()
        await descreq.delete()
        await desc.delete()


    @commands.command(name='brds', help='This command creates a Discord Announcement', aliases=['broadcast-discord', 'discordbr'])
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def brds_embed(self, ctx):
        '''Creates a Discord Announcement'''

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        dsbrping = discord.utils.get(ctx.guild.roles, id=self.bot.discordping)  # Discord BR role ID
        channel = self.bot.get_channel(self.bot.dsannchannel)  # Discord Announcements channel ID

        titlereq = await ctx.send('Waiting for a title')
        title = await self.bot.wait_for('message', check=check)

        descreq = await ctx.send('Waiting for a description')
        desc = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title=title.content, description=desc.content, color=discord.Color.from_rgb(138, 158, 252))
        embed.set_author(name="Discord News", url=self.bot.dtsite, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        await channel.send(f'New Discord Announcement! {dsbrping.mention}')
        embedsend = await channel.send(embed=embed)

        await ctx.message.delete()
        await titlereq.delete()
        await title.delete()
        await descreq.delete()
        await desc.delete()


    @commands.command(name='brnv', help='This command creates a New Version Announcement', aliases=['broadcast-newversion', 'newversion'])
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def brnv_embed(self, ctx):
        '''Creates a New Version Announcement'''

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        nvbrping = discord.utils.get(ctx.guild.roles, id=self.bot.newversionping)  # Discord BR role ID
        channel = self.bot.get_channel(self.bot.annchannel)  # Discord Announcements channel ID

        titlereq = await ctx.send('Waiting for a Version')
        title = await self.bot.wait_for('message', check=check)

        chlreq = await ctx.send('Waiting for a Changelog')
        chl = await self.bot.wait_for('message', check=check)

        linkreq = await ctx.send('Waiting for a Download link')
        link = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title=title.content, color=discord.Color.from_rgb(255, 186, 0))
        embed.set_author(name="New Version", url=self.bot.dtsite, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Changelog", value=chl.content, inline=False)
        embed.add_field(name="Download Link", value=link.content, inline=False)

        await channel.send(f'New Version Available! {nvbrping.mention}')
        embedsend = await channel.send(embed=embed)

        await ctx.message.delete()
        await titlereq.delete()
        await title.delete()
        await chlreq.delete()
        await chl.delete()
        await linkreq.delete()
        await link.delete()


def setup(bot):
    bot.add_cog(BroadcastCommands(bot))
