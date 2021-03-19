import os
from keep_alive import keep_alive
from discord.ext import commands
import discord
import json
from datetime import date, datetime



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
)



#Variables
bot.author_id = 330345930198876161	# Personal ID
bot.adminrole_id=821049483009458188	#Admin Role ID
#IF THIS IS MODIFIED, MODIFY ALSO THE IDs IN THE COGS FOR @COMMAND.HAS_ANY_ROLE()

bot.modrole_id=821049516119294002	#Mod Role ID
#IF THIS IS MODIFIED, MODIFY ALSO THE IDs IN THE COGS FOR @COMMAND.HAS_ANY_ROLE()

bot.pollping=820985795795615764	#Pollping Role ID
bot.droptopping=820985817669173248	#Droptopping Role ID
bot.discordping=822061700459003914	#Discordping Role ID
bot.annchannel=801756192480952351	#Announcements Channel ID
bot.dsannchannel=821649447502610463	#Discord Announcements Channel ID
bot.dtsite="https://blacksquare88.wixsite.com/droptop4"	#Droptop WebSite
today = date.today()
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")



#Events
@bot.event 
async def on_ready():  # When the bot is ready
	print(dt_string)
	print(bot.user, "here, I'm in")  # Prints the bot's username and identifier


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



#Commands
@bot.command(aliases=['rr'], help='This command creates a reactionrole menu')
@commands.has_any_role(bot.adminrole_id, bot.modrole_id) #Admin Role ID, Moderator Role ID
async def reactrole(ctx, emoji, role: discord.Role, *, message):

		'''Use -reactrole <emoji> <@role> <message>'''

		emb = discord.Embed(description=message)
		msg = await ctx.channel.send(embed=emb)
		await msg.add_reaction(emoji)
		await ctx.message.delete()

		with open('reactrole.json') as json_file:
				data = json.load(json_file)

				new_react_role = {'role_name': role.name, 
				'role_id': role.id,
				'emoji': emoji,
				'message_id': msg.id}

				data.append(new_react_role)

		with open('reactrole.json', 'w') as f:
				json.dump(data, f, indent=4)


@bot.command(name='bothelp', help='This command shows the help command')
async def bothelp(ctx):

		'''Bot Help Command'''
	 
		adminrole = discord.utils.get(ctx.guild.roles, id=bot.adminrole_id) #Admin Role ID
		modrole = discord.utils.get(ctx.guild.roles, id=bot.modrole_id) #Moderator Role ID

		staffemb=discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
		staffemb.set_author(name="Droptop Four", url="https://blacksquare88.wixsite.com/droptop4", icon_url=bot.user.avatar_url)
		staffemb.set_thumbnail(url=ctx.guild.icon_url)
		staffemb.add_field(name="Developer", value='`-listcogs`\nReturns a list of all the enabld cogs.\n`-load`\nLoads a cog.\n`-reload`\nReloads a cog.\n`-unload`\nUnloads a cog.', inline=False)
		staffemb.add_field(name="Reactionrole", value='`-reactrole <emoji> <@role> <message>`\nUse it to create a new reactionrole in your channel.', inline=False)
		staffemb.add_field(name="Announcements", value='`-brdt`\nCreates a Droptop Announcement.\n`-brds`\nCreates a Discord Announcement.\n`-brnv`\nCreates a New Version Announcement.', inline=False)
		staffemb.add_field(name="Polls", value='`-poll <emoji1> <emoji2>`\nCreates a poll with the 2 emojis as voting reactions.', inline=False)
		staffemb.add_field(name="Utilities", value='`-ping`\nReturns the latency of the bot.\n`-bothelp`\nShows this message.', inline=False)

		memberemb=discord.Embed(title='Bot Commands', color=discord.Color.from_rgb(75, 215, 100))
		memberemb.set_author(name="Droptop Four", url="https://blacksquare88.wixsite.com/droptop4", icon_url=bot.user.avatar_url)
		memberemb.set_thumbnail(url=ctx.guild.icon_url)
		memberemb.add_field(name="Utilities", value='`-ping`\nReturns the latency of the bot.\n`-bothelp`\nShows this message.', inline=False)
		memberemb.set_footer(text="Other commands are coming out soon, so saty tuned!!\nObviously every suggestion is welcome!")

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
	'cogs.cog_info',	# folder.cog_name
	'cogs.cog_polls', # folder.cog_name
	'cogs.cog_br',		# folder.cog_name
	'cogs.cog_help',	# folder.cog_name
]


if __name__ == '__main__':  # Ensures this is the file being ran
	for extension in extensions:
		bot.load_extension(extension)  # Loades extensions in extensions list.



#Run
keep_alive()  # Starts a webserver to be pinged.
bot.run(os.getenv("token"))  # Starts the bot