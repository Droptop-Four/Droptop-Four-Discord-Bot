'''
    Project name: Droptop Four Discord Bot
    Discord: https://discord.gg/hQGDm4F5Ef
    Author: Bunz (bunz#3066)
    Date created: 21/10/2022
    Bot Version: 3.5
    Python Version: 3.10.4
    Cogs: 6
'''



import discord, os, threading
from discord.ext import commands

from http import server
from urllib import request
import json
import re
import pymongo
from pymongo import MongoClient

import logging
import logging.handlers

from utils import date_time, command_mention

# from dotenv import load_dotenv



# load_dotenv()

main_prefix = ()

bot = commands.Bot(
	command_prefix=main_prefix,
	intents=discord.Intents.all(),
	description="Official discord bot for the Droptop Four discord server",
	activity=discord.Activity(type=discord.ActivityType.listening, name="slash commands"),
	strip_after_prefix=True,
	case_insensitive=True
)


cluster = MongoClient(os.getenv("mongodb_id"))
db = cluster[os.getenv("db_cluster")]
config_collection = db["Config"]
commands_collection = db["Commands"]

bot.configs = config_collection.find_one({},{"_id": 0})

bot.cari_logo = "https://raw.githubusercontent.com/Droptop-Four/GlobalData/v3/data/logos/cariboudjan_logo.png"
bot.droptopfour_logo = "https://raw.githubusercontent.com/Droptop-Four/GlobalData/v3/data/logos/droptopfour_logo.png"



# HTTP request handler
class Server(server.BaseHTTPRequestHandler):
	# Override the log_request function to prevent spammy logging output
	def log_request(self, code="", size=""):
		pass

	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.send_header("Cache-Control", "max-age=180")
		self.end_headers()
		# Set the content of the website
		self.wfile.write(
			f"<!DOCTYPE html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width'><title>Discord Bot</title></head>{bot.user} is alive!<br>Latency: {round(bot.latency*1000)}ms<br>Servers: {len(bot.guilds)}</html>".encode()
		)


@bot.event
async def on_thread_create(thread):
	if thread.parent.id == 1019694544876482670:
		await thread.add_tags(discord.Object(1030636641951420457))

		await thread.starter_message.pin()

		messaggio = await thread.send(f"To close this message use {command_mention('solved', '1078282304876707891')}")

		await messaggio.pin()


@bot.event
async def on_ready():
	print(f"{date_time()} Logged in as {bot.user} (ID: {bot.user.id})")
	logging.info(f"{date_time()} Logged in as {bot.user} (ID: {bot.user.id})")
	for guild in bot.guilds:
		print("Connected to server: {}".format(guild))
		logging.info("Connected to server: {}".format(guild))
	print("------")
	logging.info("------")

	# Start the http server at port 80, using the handler class created earlier
	threading.Thread(target=server.HTTPServer(("", 80), Server).serve_forever).start()
	try:
		# Add repl to up.repl.link so it can be kept alive
		request.urlopen(f"https://ced0775a-02a8-41d5-a6cf-14815ad4a73e.id.repl.co/add?repl={os.environ['REPL_SLUG']}&author={os.environ['REPL_OWNER']}")
	except:
		pass


@bot.event
async def on_message(msg):
	if msg.author.bot:
		return
	if re.fullmatch(rf"<@!?{bot.user.id}>", msg.content):
		return await msg.channel.send(f"You can use me with slash commands now!\nType `/` to see a list of possible commands.")
	#if msg.type is discord.MessageType.pins_add:
		#if msg.channel.type is discord.ChannelType.public_thread:
			#if msg.channel.parent.id == 1019694544876482670:
				#await msg.delete()
	
	return await bot.process_commands(msg)


@bot.event
async def on_app_command_completion(interaction, command):
	post = {"UserID": interaction.user.id, "UsersID": interaction.user.name, "channelID": interaction.channel_id, "channel": interaction.channel.name, "command": "/"+command.qualified_name}
	commands_collection.insert_one(post)
	

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")
    raise error


@bot.event
async def on_raw_reaction_add(payload):
	if payload.member.bot:
		pass
	else:
		with open("reactrole.json") as react_file:
			data = json.load(react_file)
			for x in data:
				if x["emoji"] == payload.emoji.name:
					role = discord.utils.get(bot.get_guild(
						payload.guild_id).roles, id=x["role_id"])
					await payload.member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
	with open("reactrole.json") as react_file:
		data = json.load(react_file)
		for x in data:
			if x["emoji"] == payload.emoji.name:
				role = discord.utils.get(bot.get_guild(
					payload.guild_id).roles, id=x["role_id"])
				await bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)


@bot.event
async def setup_hook():
	extensions = [
		"cogs.cog_admin",
		"cogs.cog_dev",
		"cogs.cog_mod",
		"cogs.cog_droptop",
		"cogs.cog_sugg",
		"cogs.cog_misc"
	]
	for extension in extensions:
		await bot.load_extension(extension)
	bot.tree.clear_commands(guild=discord.Object(id=bot.configs["server_id"]))
	await bot.tree.sync()



@bot.tree.error
async def on_tree_error(interaction, error):
    try:
        await interaction.response.send_message(f"Error: {error}", ephemeral=True)
    except discord.InteractionResponded:
        await interaction.followup.send(f"Error: {error}", ephemeral=True)
    raise error



logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)



try:
	bot.run(bot.configs["discord_token"])
except discord.HTTPException as err:
	if err.status == 429:
		print("Rate limit detected🙄Restarting repl.")
		# Kill the init process with signal 1, potentially causing the repl to restart and switch to an IP that isn"t rate limited
		os.kill(1, 1)
	print(err)
