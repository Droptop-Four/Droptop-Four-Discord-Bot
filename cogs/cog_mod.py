import os
import discord
from discord.ext import commands
import time
import pymongo
from pymongo import MongoClient


cluster = MongoClient(os.getenv("mongodb_id"))
db = cluster["Discord_Droptop"]
collection_bw = db["BannedWords"]


class ModCommands(commands.Cog, name='Moderation'):
    '''These are the Mod Commands'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        elif message.author.id == self.bot.author_id:
            return
        elif message.author.id == self.bot.cari_id:
            return
        else:
            with open('bannedwords.txt') as file:
                file = file.read().split()
            for bannedword in file:
                if bannedword in message.content.lower():
                    await message.delete()

    @commands.command(name='bannedwords', aliases=['bw', 'banwords', 'banword', 'bannedword'])
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def bannedwords(self, ctx, arg1=None, arg2=None):
        bwls = ['ls', 'list', 'all', ]
        bwadd = ['add', ]
        bwremove = ['rm', 'remove', 'delete', ]
        if arg1 is None:
            mydoc = collection_bw.find()
            f = open("bannedwords.txt", "w")
            for x in mydoc:
                query = x['name']+' '
                f.write(query)
            f.close()
            f = open("bannedwords.txt", "r")
            result = f.read()
            if result:
                await ctx.send('The banned words are: '+result)
            else:
                await ctx.send('Currently there are no banned words.')
        if arg1 in bwls:
            mydoc = collection_bw.find()
            f = open("bannedwords.txt", "w")
            for x in mydoc:
                query = x['name']+' '
                f.write(query)
            f.close()
            f = open("bannedwords.txt", "r")
            if result:
                await ctx.send('The banned words are: '+result)
            else:
                await ctx.send('Currently there are no banned words.')
        elif arg1 in bwadd:
            if arg2 is None:
                await ctx.send('You need to add a word to be added to the banned words list.')
            else:
                arg2 = arg2.lower()
                post = {"UserID": ctx.author.id,
                        "sID": ctx.author.display_name, "name": arg2}
                collection_bw.insert_one(post)
                await ctx.send('`{0}` was added to the banned words list.'.format(arg2))
                mydoc = collection_bw.find()
                f = open("bannedwords.txt", "w")
                for x in mydoc:
                    query = x['name']+' '
                    f.write(query)
                f.close()
        elif arg1 in bwremove:
            if arg2 is None:
                await ctx.send('You need to add a word to be removed from the banned words list.')
            else:
                arg2 = arg2.lower()
                query = {"name": arg2}
                collection_bw.delete_one(query)
                await ctx.send('`{0}` was removed from the banned words list.'.format(arg2))
                mydoc = collection_bw.find()
                f = open("bannedwords.txt", "w")
                for x in mydoc:
                    query = x['name']+' '
                    f.write(query)
                f.close()
        else:
            pass

    @commands.command(name='kick', aliases=[])
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.kick(user=member, reason=reason)
        channel = self.bot.get_channel(self.bot.modlogchannel)
        embed = discord.Embed(
            title=f"{ctx.author.name} kicked: {member.name}", description=reason)
        await channel.send(embed=embed)

    @commands.command(name='ban', aliases=[])
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.ban(user=member, reason=reason)
        channel = self.bot.get_channel(self.bot.modlogchannel)
        embed = discord.Embed(
            title=f"{ctx.author.name} banned: {member.name}", description=reason)
        await channel.send(embed=embed)

    @commands.command(name='unban', aliases=[])
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def unban(self, ctx, member, *, reason=None):
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)
        channel = self.bot.get_channel(self.bot.modlogchannel)
        embed = discord.Embed(
            title=f"{ctx.author.name} unbanned: {member.name}", description=reason)
        await channel.send(embed=embed)

    @commands.command(name='purge', aliases=[])
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def purge(self, ctx, amount=15):
        await self.bot.wait_until_ready()
        await ctx.channel.purge(limit=amount+1)
        channel = self.bot.get_channel(self.bot.modlogchannel)
        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}", description=f"{amount} messages were cleared")
        await channel.send(embed=embed)

    @commands.command(name='infodesk', help='This command returns a welcome message')
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def infodesk(self, ctx):
        channel = self.bot.get_channel(self.bot.infodeskchannel)
        embed = discord.Embed(
            title="WELCOME!!", description="Welcome to the Official Droptop Four Discord Server!!", color=0x60d96b)
        embed.set_author(name="Droptop Four", url="https://www.droptopfour.com",
                         icon_url="https://cdn.discordapp.com/icons/800124057923485728/a_4be318be5515b8bcc1bc8f5a68e15e46.webp?size=1024")
        embed.add_field(name="**What is Droptop?**", value="Droptop Four is a popular dropdown app launcher for Windows & Rainmeter. It is available in two version, a `Basic` one, free, and a `Supporter` one, with a 'pay what you want' donation.  Both versions have 14 system tray apps, the Always Show option to make it accessible everywhere on top of your desktop and a lot more.", inline=False)
        embed.add_field(name="**Further Informations**",
                        value="If you have further informations you can use the `-info` command in <#{}>".format(self.bot.botchatchannel), inline=False)
        embed.set_footer(
            text="If you have other questions, feel free to ask them in the server!")
        await ctx.message.delete()
        await channel.send(embed=embed)

    @commands.command(name='bothelpexample', help='This command shows the help command', aliases=['bhe', 'b-h-e', 'helpe', 'he', 'helpexample'])
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def bothelp(self, ctx):

        '''Bot Help Command'''

        channel = self.bot.get_channel(self.bot.botcommandschannel)

        helpexample = discord.Embed(
            title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
        helpexample.set_author(
            name="Droptop Four", url="https://blacksquare88.wixsite.com/droptop4", icon_url=self.bot.user.avatar_url)
        helpexample.set_thumbnail(url=ctx.guild.icon_url)
        helpexample.add_field(name='Droptop', value='`{0}info`\nShows info about the Droptop Four bar.\n`{0}download`\nShows the Droptop Four download possibilities.\n`{0}faq`\nShows the FAQ link.\n`{0}beta`\nThis command sends you informations on how to apply to the beta-testing program.'.format(
            (self.bot.command_prefix)), inline=False)
        helpexample.add_field(name="Suggestions", value='`{0}suggest`\nSends a suggestion to <#{1}>.'.format(
            (self.bot.command_prefix), (self.bot.suggchannel)), inline=False)
        helpexample.add_field(name="Utilities", value='`{0}ping`\nReturns the latency of the bot.\n`{0}bothelp`\nShows this message.'.format(
            self.bot.command_prefix), inline=False)
        helpexample.set_footer(text="Every command suggestion is welcome!")

        await channel.send(embed=helpexample)


def setup(bot):
    bot.add_cog(ModCommands(bot))
