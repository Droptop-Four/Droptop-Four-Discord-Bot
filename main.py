'''
    Project name: Droptop Four Discord Bot
    Discord: https://discord.gg/hQGDm4F5Ef
    Author: Bunz (bunz#3066)
    Date created: 19/03/2021
    Date last modified: 09/09/2021
    Bot Version: 2.6
    Python Version: 3.8.10
    Cogs: 7
'''


import os
from keep_alive import keep_alive
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, Select, SelectOption
# from discord_slash import SlashCommand
import discord
import json
from datetime import date, datetime
import time
import pymongo
from pymongo import MongoClient


# init
help_command = commands.DefaultHelpCommand(
    no_category='Utilities'
)


bot = commands.Bot(
    command_prefix="-",  # Change to desired prefix
    case_insensitive=True,  # Commands aren't case-sensitive
    intents=discord.Intents.all(),
    # help_command = help_command,
    help_command=None
)  # Bot initialization

# slash = SlashCommand(bot, sync_commands=True)

# Variables
bot.author_id = int(os.getenv("author_id"))  # Personal ID
bot.server_id = int(os.getenv("server_id"))  # Server ID
bot.cari_id = int(os.getenv("cari_id"))  # Cari ID
bot.adminrole_id = int(os.getenv("adminrole_id"))  # Admin Role ID
# IF THIS IS MODIFIED, MODIFY ALSO THE IDs IN THE COGS FOR @COMMAND.HAS_ANY_ROLE()
bot.modrole_id = int(os.getenv("modrole_id"))  # Mod Role ID
# IF THIS IS MODIFIED, MODIFY ALSO THE IDs IN THE COGS FOR @COMMAND.HAS_ANY_ROLE()
bot.pollping = int(os.getenv("pollping"))  # Pollping Role ID
bot.droptopping = int(os.getenv("droptopping"))  # Droptopping Role ID
bot.discordping = int(os.getenv("discordping"))  # Discordping Role ID
bot.newversionping = int(os.getenv("newversionping"))  # Newversionping Role ID
bot.betarole = int(os.getenv("betarole"))  # Betatester Role ID
bot.annchannel = int(os.getenv("annchannel"))  # Announcements Channel ID
bot.dsannchannel = int(os.getenv("dsannchannel"))  # Discord Announcements Channel ID
bot.infodeskchannel = int(os.getenv("infodeskchannel"))  # Infodesk Channel ID
bot.botcommandschannel = int(os.getenv("botcommandschannel"))  # BotCommand Channel ID
bot.suggchannel = int(os.getenv("suggchannel"))  # Suggestion Log Channel ID
bot.betachannel = int(os.getenv("betachannel"))  # Betarequest Log Channel ID
bot.botchatchannel = int(os.getenv("botchatchannel"))  # Botchat Channel ID
bot.modlogchannel = int(os.getenv("modlogchannel"))  # Modlog Channel ID
bot.dtsite = os.getenv("dtsite")  # Droptop WebSite
today = date.today()
now = datetime.now()
date_time = now.strftime("%d/%m/%Y %H:%M:%S")  # Day/Month/Year Hours:Minutes:Seconds


# Database
cluster = MongoClient(os.getenv("mongodb_id"))
db = cluster["Discord_Droptop"]
collection = db["MessageLog"]


# Events
@bot.event
async def on_ready():  # When the bot is ready
    print(date_time)  # Prints the date and time
    print(bot.user, "here, I'm in")  # Prints the bot's username and identifier
    for guild in bot.guilds:  # Prints all the servers the bot is in
        print("Connected to server: {}".format(guild))
    print("------")
    DiscordComponents(bot)
    # change_status.start()


# @tasks.loop()
# async def change_status():
# 	while True:
# 		await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='over you | -help, -info'))
# 		time.sleep(10)


@bot.event
async def on_raw_reaction_add(payload):

    if payload.member.bot:
        pass

    else:
        with open('reactrole.json') as react_file:
            data = json.load(react_file)
            for x in data:
                if x['emoji'] == payload.emoji.name:
                    role = discord.utils.get(bot.get_guild(
                        payload.guild_id).roles, id=x['role_id'])
                    await payload.member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):

    with open('reactrole.json') as react_file:
        data = json.load(react_file)
        for x in data:
            if x['emoji'] == payload.emoji.name:
                role = discord.utils.get(bot.get_guild(
                    payload.guild_id).roles, id=x['role_id'])
                await bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)


@bot.command(name='reactionrole', aliases=['rr', 'reactrole'], help='This command creates a reactionrole in the channel')
# Admin Role ID, Mod Role ID
@commands.has_any_role(800217789343727657, 801741190227165236)
async def reactrole(ctx, emoji, role: discord.Role, *, message):
    '''Creates a reactionrole in the channel'''

    emb = discord.Embed(description=message)
    msg = await ctx.channel.send(embed=emb)
    await msg.add_reaction(emoji)

    with open('reactrole.json') as json_file:
        data = json.load(json_file)

        new_react_role = {'role_name': role.name, 'role_id': role.id, 'emoji': emoji, 'message_id': msg.id}

        data.append(new_react_role)

    with open('reactrole.json', 'w') as f:
        json.dump(data, f, indent=4)


@reactrole.error
async def _rero_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Syntax Error', color=0xFF2E00)
        embed.add_field(name='{}reactrole command'.format(bot.command_prefix), value='{}reactrole <emoji> <@role> <message>'.format(bot.command_prefix), inline=False)
        embsend = await ctx.send(embed=embed)
        time.sleep(5)
        await ctx.message.delete()
        time.sleep(15)
        await embsend.delete()


@bot.command(name='bothelp', help='This command shows the help command', aliases=['bh', 'b-h', 'help'])
async def bothelp(ctx):
    '''Shows the help command'''

    adminrole = discord.utils.get(ctx.guild.roles, id=bot.adminrole_id)  # Admin Role ID
    modrole = discord.utils.get(ctx.guild.roles, id=bot.modrole_id)  # Moderator Role ID

    staffemb = discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
    staffemb.set_author(name="Droptop Four", url=bot.dtsite, icon_url=bot.user.avatar_url)
    staffemb.set_thumbnail(url=ctx.guild.icon_url)
    staffemb.add_field(name="Developer", value='`{0}listcogs`\nReturns a list of all the enabld cogs.\n`{0}load`\nLoads a cog.\n`{0}reload`\nReloads a cog.\n`{0}unload`\nUnloads a cog.'.format(bot.command_prefix), inline=False)
    staffemb.add_field(name="Reactionrole", value='`{0}reactrole <emoji> <@role> <message>`\nUse it to create a new reactionrole in your current channel.'.format(bot.command_prefix), inline=False)
    staffemb.add_field(name="Announcements", value='`{3}brdt`\nCreates a Droptop Announcement in <#{0}>.\n`{3}brds`\nCreates a Discord Announcement in <#{1}>.\n`{3}brnv`\nCreates a New Version Announcement <#{2}>.'.format((bot.annchannel), (bot.dsannchannel), (bot.annchannel), (bot.command_prefix)), inline=False)
    staffemb.add_field(name="Polls", value='`{0}poll <emoji1> <emoji2>`\nCreates a poll with the 2 emojis as voting reactions in your current channel.'.format(bot.command_prefix), inline=False)
    staffemb.add_field(name="Moderation", value='`{0}bannedwords (arg1) (arg2)`\nIf the two args are empty and if `arg1=list` the banned words list will be shown, if `arg1=add` `arg`2 will be added to the banned words list, if `arg1=remove` `arg2` will be removed from the banned words list. (`arg1` has to be lowercase but `arg2` has to be a single word and will be lowered in any case as every message sent)\n`{0}kick <memberMention>`\nKiks the specified user.\n`{0}ban <memberMention>`\nBans the specified member.\n`{0}unban <memberMention>`\nUnbans the specified user.\n`{0}purge <number>`\nPurges the specified number of messages from teh channel. If no number is given 15 messages will be deleted.\n`{0}infodesk`\nSends an infodesk message in the <#{1}> channel\n`{0}helpexample`\nSends the bot commands in <#{2}>'.format((bot.command_prefix), (bot.infodeskchannel), (bot.botcommandschannel)), inline=False)
    staffemb.add_field(name='Droptop', value='`{0}info`\nShows info about the Droptop Four bar.\n`{0}download`\nShows the Droptop Four download possibilities.\n`{0}faq`\nShows the FAQ link.\n`{0}beta`\nThis command sends you informations on how to apply to the beta-testing program.'.format(bot.command_prefix), inline=False)
    staffemb.add_field(name="Utilities", value='`{0}ping`\nReturns the latency of the bot.\n`{0}bothelp`\nShows this message.'.format(bot.command_prefix), inline=False)

    memberemb = discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
    memberemb.set_author(name="Droptop Four", url=bot.dtsite, icon_url=bot.user.avatar_url)
    memberemb.set_thumbnail(url=ctx.guild.icon_url)
    memberemb.add_field(name='Droptop', value='`{0}info`\nShows info about the Droptop Four bar.\n`{0}download`\nShows the Droptop Four download possibilities.\n`{0}faq`\nShows the FAQ link.\n`{0}beta`\nThis command sends you informations on how to apply to the beta-testing program.'.format((bot.command_prefix)), inline=False)
    memberemb.add_field(name="Suggestions", value='`{0}suggest`\nSends a suggestion to <#{1}>.'.format((bot.command_prefix), (bot.suggchannel)), inline=False)
    memberemb.add_field(name="Utilities", value='`{0}ping`\nReturns the latency of the bot.\n`{0}bothelp`\nShows this message.'.format(bot.command_prefix), inline=False)
    memberemb.set_footer(text="Every command suggestion is welcome!")

    if adminrole in ctx.author.roles:
        await ctx.send(embed=staffemb)
    elif modrole in ctx.author.roles:
        await ctx.send(embed=staffemb)
    else:
        await ctx.send(embed=memberemb)


# @slash.slash(name="help", description="Returns all commands")
# async def slashbothelp(ctx):
# 		'''Shows the help command'''

# 		adminrole = discord.utils.get(ctx.guild.roles, id=bot.adminrole_id) #Admin Role ID
# 		modrole = discord.utils.get(ctx.guild.roles, id=bot.modrole_id) #Moderator Role ID

# 		staffemb=discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
# 		staffemb.set_author(name="Droptop Four", url=bot.dtsite, icon_url=bot.user.avatar_url)
# 		staffemb.set_thumbnail(url=ctx.guild.icon_url)
# 		staffemb.add_field(name="Developer", value='`{0}listcogs`\nReturns a list of all the enabld cogs.\n`{0}load`\nLoads a cog.\n`{0}reload`\nReloads a cog.\n`{0}unload`\nUnloads a cog.'.format(bot.command_prefix), inline=False)
# 		staffemb.add_field(name="Reactionrole", value='`{0}reactrole <emoji> <@role> <message>`\nUse it to create a new reactionrole in your current channel.'.format(bot.command_prefix), inline=False)
# 		staffemb.add_field(name="Announcements", value='`{3}brdt`\nCreates a Droptop Announcement in <#{0}>.\n`{3}brds`\nCreates a Discord Announcement in <#{1}>.\n`{3}brnv`\nCreates a New Version Announcement <#{2}>.'.format((bot.annchannel), (bot.dsannchannel), (bot.annchannel), (bot.command_prefix)), inline=False)
# 		staffemb.add_field(name="Polls", value='`{0}poll <emoji1> <emoji2>`\nCreates a poll with the 2 emojis as voting reactions in your current channel.'.format(bot.command_prefix), inline=False)
# 		staffemb.add_field(name="Moderation", value='`{0}bannedwords (arg1) (arg2)`\nIf the two args are empty and if `arg1=list` the banned words list will be shown, if `arg1=add` `arg`2 will be added to the banned words list, if `arg1=remove` `arg2` will be removed from the banned words list. (`arg1` has to be lowercase but `arg2` has to be a single word and will be lowered in any case as every message sent)\n`{0}kick <memberMention>`\nKiks the specified user.\n`{0}ban <memberMention>`\nBans the specified member.\n`{0}unban <memberMention>`\nUnbans the specified user.\n`{0}purge <number>`\nPurges the specified number of messages from teh channel. If no number is given 15 messages will be deleted.'.format(bot.command_prefix), inline=False)
# 		staffemb.add_field(name='Droptop',value='`{0}info`\nShows info about the Droptop Four bar.\n`{0}download`\nShows the Droptop Four download possibilities.\n`{0}faq`\nShows the FAQ link.\n`{0}beta`\nThis command sends you informations on how to apply to the beta-testing program.'.format(bot.command_prefix), inline=False)
# 		staffemb.add_field(name="Utilities", value='`{0}ping`\nReturns the latency of the bot.\n`{0}bothelp`\nShows this message.'.format(bot.command_prefix), inline=False)

# 		memberemb=discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
# 		memberemb.set_author(name="Droptop Four", url=bot.dtsite, icon_url=bot.user.avatar_url)
# 		memberemb.set_thumbnail(url=ctx.guild.icon_url)
# 		memberemb.add_field(name='Droptop',value='`{0}info`\nShows info about the Droptop Four bar.\n`{0}download`\nShows the Droptop Four download possibilities.\n`{0}faq`\nShows the FAQ link.\n`{0}beta`\nThis command sends you informations on how to apply to the beta-testing program.'.format((bot.command_prefix)), inline=False)
# 		memberemb.add_field(name="Suggestions", value='`{0}suggest`\nSends a suggestion to <#{1}>.'.format((bot.command_prefix),(bot.suggchannel)), inline=False)
# 		memberemb.add_field(name="Utilities", value='`{0}ping`\nReturns the latency of the bot.\n`{0}bothelp`\nShows this message.'.format(bot.command_prefix), inline=False)
# 		memberemb.set_footer(text="Other commands are coming out soon, so saty tuned!!\nObviously every suggestion is welcome!")

# 		if adminrole in ctx.author.roles:
# 			await ctx.send(embed=staffemb)
# 		elif modrole in ctx.author.roles:
# 			await ctx.send(embed=staffemb)
# 		else:
# 			await ctx.send(embed=memberemb)


# Extensions
extensions = [
    'cogs.cog_dev',		# folder.cog_name
    'cogs.cog_mod',		# folder.cog_name
    'cogs.cog_droptop',  # folder.cog_name
    'cogs.cog_polls',  # folder.cog_name
    'cogs.cog_br',		# folder.cog_name
    'cogs.cog_sugg',  # folder.cog_name
    'cogs.cog_misc',  # folder.cog_name
]


if __name__ == '__main__':  # Ensures this is the file being ran
    for extension in extensions:
        bot.load_extension(extension)  # Loades extensions in extensions list.


# Run
keep_alive()  # Starts a webserver to be pinged.
bot.run(os.getenv("ds_token"))  # Starts the bot
