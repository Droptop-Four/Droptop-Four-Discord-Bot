import os
from keep_alive import keep_alive
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, Select, SelectOption
import discord
import json
from datetime import date, datetime
import time
import pymongo
from pymongo import MongoClient


#init
help_command = commands.DefaultHelpCommand(
    no_category = 'Utilities'
)


bot = commands.Bot(
	command_prefix="-",	# Change to desired prefix
	case_insensitive=True,	# Commands aren't case-sensitive
	intents=discord.Intents.all(),
	# help_command = help_command,
	help_command = None
)	#Bot initialization



#Variables
bot.author_id = 330345930198876161	# Personal ID
bot.serverid=800124057923485728		# Server ID
bot.cari_id = 584542239900827665	# Cari ID
bot.adminrole_id=800217789343727657	# Admin Role ID
#IF THIS IS MODIFIED, MODIFY ALSO THE IDs IN THE COGS FOR @COMMAND.HAS_ANY_ROLE()
bot.modrole_id=801741190227165236	# Mod Role ID
#IF THIS IS MODIFIED, MODIFY ALSO THE IDs IN THE COGS FOR @COMMAND.HAS_ANY_ROLE()
bot.pollping=822061196567248916			# Pollping Role ID
bot.droptopping=822061436690890752		# Droptopping Role ID
bot.discordping=822061367309631499		# Discordping Role ID
bot.newversionping=822061500747218974   # Newversionping Role ID
bot.betarole=800130009947045901			# Betatester Role ID
bot.annchannel=801785532035760138		# Announcements Channel ID
bot.dsannchannel=801785435198193765		# Discord Announcements Channel ID
bot.suggchannel=802849786717274112  	# Suggestion Log Channel ID
bot.betachannel=859714062769455104		# Betarequest Log Channel ID
bot.dtsite="https://blacksquare88.wixsite.com/droptop4"	#Droptop WebSite
today = date.today()
now = datetime.now()
date_time = now.strftime("%d/%m/%Y %H:%M:%S")	# Day/Month/Year Hours:Minutes:Seconds
#Database
cluster = MongoClient(os.getenv("client_id"))
db = cluster["Discord_Droptop"]
collection = db["MessageLog"]



#Events
@bot.event 
async def on_ready():	# When the bot is ready
	print(date_time)	# Prints the date and time
	print(bot.user, "here, I'm in")	# Prints the bot's username and identifier
	for guild in bot.guilds:	# Prints all the servers the bot is in
		print ("Connected to server: {}".format(guild))
	print("------")
	DiscordComponents(bot)
	# change_status.start()


# @bot.event
# async def on_message(message):
# 		await bot.process_commands(message)



@bot.event
async def on_raw_reaction_add(payload):

    if payload.member.bot:
        pass

    else:
        with open('reactrole.json') as react_file:
            data = json.load(react_file)
            for x in data:
                if x['emoji'] == payload.emoji.name:
                    role = discord.utils.get(bot.get_guild(payload.guild_id).roles, id=x['role_id'])
                    await payload.member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):


	with open('reactrole.json') as react_file:
		data = json.load(react_file)
		for x in data:
			if x['emoji'] == payload.emoji.name:
				role = discord.utils.get(bot.get_guild(payload.guild_id).roles, id=x['role_id'])
				await bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)
                    



@bot.command(name='reactionrole',aliases=['rr', 'reactrole'])
@commands.has_any_role(800217789343727657, 801741190227165236)	#Admin Role ID, Mod Role ID 
async def reactrole(ctx, emoji, role: discord.Role, *, message):

    emb = discord.Embed(description=message)
    msg = await ctx.channel.send(embed=emb)
    await msg.add_reaction(emoji)
    
    with open('reactrole.json') as json_file:
        data = json.load(json_file)

        new_react_role = {'role_name': role.name, 
        'role_id': role.id,
        'emoji': emoji,
        'message_id': msg.id}

        data.append(new_react_role)

    with open('reactrole.json', 'w') as f:
        json.dump(data, f, indent=4)



@reactrole.error
async def _rero_error(ctx, error):
    if isinstance (error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Syntax Error', color=0xFF2E00)
        embed.add_field(name='{}reactrole command'.format(bot.command_prefix), value='{}reactrole <emoji> <@role> <message>'.format(bot.command_prefix), inline=False)
        embsend=await ctx.send(embed=embed)
        time.sleep(5)
        await ctx.message.delete()
        time.sleep(15)
        await embsend.delete()



@bot.command(name='bothelp', help='This command shows the help command', aliases=['bh', 'b-h','help'])
async def bothelp(ctx):

		'''Bot Help Command'''
	 
		adminrole = discord.utils.get(ctx.guild.roles, id=bot.adminrole_id) #Admin Role ID
		modrole = discord.utils.get(ctx.guild.roles, id=bot.modrole_id) #Moderator Role ID

		staffemb=discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
		staffemb.set_author(name="Droptop Four", url="https://blacksquare88.wixsite.com/droptop4", icon_url=bot.user.avatar_url)
		staffemb.set_thumbnail(url=ctx.guild.icon_url)
		staffemb.add_field(name="Developer", value='`{0}listcogs`\nReturns a list of all the enabld cogs.\n`{0}load`\nLoads a cog.\n`{0}reload`\nReloads a cog.\n`{0}unload`\nUnloads a cog.'.format(bot.command_prefix), inline=False)
		staffemb.add_field(name="Reactionrole", value='`{0}reactrole <emoji> <@role> <message>`\nUse it to create a new reactionrole in your current channel.'.format(bot.command_prefix), inline=False)
		staffemb.add_field(name="Announcements", value='`{3}brdt`\nCreates a Droptop Announcement in <#{0}>.\n`{3}brds`\nCreates a Discord Announcement in <#{1}>.\n`{3}brnv`\nCreates a New Version Announcement <#{2}>.'.format((bot.annchannel), (bot.dsannchannel), (bot.annchannel), (bot.command_prefix)), inline=False)
		staffemb.add_field(name="Polls", value='`{0}poll <emoji1> <emoji2>`\nCreates a poll with the 2 emojis as voting reactions in your current channel.'.format(bot.command_prefix), inline=False)
		staffemb.add_field(name="Moderation", value='`{0}bannedwords <arg1> <arg2>`\nIf the two args are empty and if `arg1=list` the banned words list will be shown, if `arg1=add` `arg`2 will be added to the banned words list, if `arg1=remove` `arg2` will be removed from the banned words list. (`arg1` has to be lowercase but `arg2` has to be a single word and will be lowered in any case as every message sent)\n`{0}kick <memberMention>`\nKiks the specified user.\n`{0}ban <memberMention>`\nBans the specified member.\n`{0}unban <memberMention>`\nUnbans the specified user.\n`{0}purge <number>`\nPurges the specified number of messages from teh channel. If no number is given 15 messages will be deleted.'.format(bot.command_prefix), inline=False)
		staffemb.add_field(name='Droptop',value='`{0}info`\nShows info about the Droptop Four bar.\n`{0}download`\nShows the Droptop Four download possibilities.\n`{0}faq`\nShows the FAQ link.\n`{0}beta`\nThis command sends you informations on how to apply to the beta-testing program.'.format((bot.command_prefix)), inline=False)
		staffemb.add_field(name="Utilities", value='`{0}ping`\nReturns the latency of the bot.\n`{0}bothelp`\nShows this message.'.format(bot.command_prefix), inline=False)

		memberemb=discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
		memberemb.set_author(name="Droptop Four", url="https://blacksquare88.wixsite.com/droptop4", icon_url=bot.user.avatar_url)
		memberemb.set_thumbnail(url=ctx.guild.icon_url)
		memberemb.add_field(name='Droptop',value='`{0}info`\nShows info about the Droptop Four bar.\n`{0}download`\nShows the Droptop Four download possibilities.\n`{0}faq`\nShows the FAQ link.\n`{0}beta`\nThis command sends you informations on how to apply to the beta-testing program.'.format((bot.command_prefix)), inline=False)
		memberemb.add_field(name="Suggestions", value='`{0}suggest`\nSends a suggestion to <#{1}>.'.format((bot.command_prefix),(bot.suggchannel)), inline=False)
		memberemb.add_field(name="Utilities", value='`{0}ping`\nReturns the latency of the bot.\n`{0}bothelp`\nShows this message.'.format(bot.command_prefix), inline=False)
		memberemb.set_footer(text="Other commands are coming out soon, so stay tuned!!\nObviously every suggestion is welcome!")

		if adminrole in ctx.author.roles:
			await ctx.send(embed=staffemb)
		elif modrole in ctx.author.roles:
			await ctx.send(embed=staffemb)
		else:
			await ctx.send(embed=memberemb)



#Extensions
extensions = [
	'cogs.cog_dev',		# folder.cog_name
	'cogs.cog_mod',		# folder.cog_name
	'cogs.cog_droptop',	# folder.cog_name
	'cogs.cog_polls',	# folder.cog_name
	'cogs.cog_br',		# folder.cog_name
	'cogs.cog_sugg',	# folder.cog_name
	'cogs.cog_misc',	# folder.cog_name
]


if __name__ == '__main__':  # Ensures this is the file being ran
	for extension in extensions:
		bot.load_extension(extension)  # Loades extensions in extensions list.



#Run
keep_alive()  # Starts a webserver to be pinged.
bot.run(os.getenv("token"))  # Starts the bot