
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.tasks import loop

from utils import github_reader, update_json, version_validator
import emoji as ej
import json, os, time, traceback
import pymongo
from pymongo import MongoClient

cluster = MongoClient(os.getenv("mongodb_id"))
db = cluster[os.getenv("db_cluster")]
config_collection = db["Config"]

configs = config_collection.find_one({},{"_id": 0})


class NewVersion(discord.ui.Modal, title="New Version"):

	version = discord.ui.TextInput(
		label="Version",
		placeholder="Use only numbers and dots. ex '4.309.58'",
	)

	features = discord.ui.TextInput(
		label="New Features",
		style=discord.TextStyle.paragraph,
		placeholder="Type new features here...",
		required=False,
	)

	modifications = discord.ui.TextInput(
		label="Modifications",
		style=discord.TextStyle.paragraph,
		placeholder="Type modifications here...",
		required=False,
	)

	bugfixes = discord.ui.TextInput(
		label="Bug Fixes",
		style=discord.TextStyle.paragraph,
		placeholder="Type bug fixes here...",
		required=False,
	)

	async def on_submit(self, interaction: discord.Interaction):
		dtbrping = discord.utils.get(interaction.guild.roles, id=configs["newversion_role"])
		annchannel = interaction.guild.get_channel(configs["announcements_channel"])

		if version_validator(self.version.value):
			version = self.version.value[:5]

			await interaction.response.send_message(f"Version {self.version.value} of droptop is being released", ephemeral=True)
			
			updated_json = update_json("version", version = version)
	
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url="https://github.com/Droptop-Four/Update/raw/main/Droptop%20Update.rmskin")
			view.add_item(item=download_button)
	
			embed = discord.Embed(title=f"📢 Droptop Four {self.version.value}", url="https://github.com/Droptop-Four/Update/releases/tag/Update", color=0x2F3136)
			if self.features.value:
				embed.add_field(name="New features <:New:1041649766175625296>", value=self.features.value, inline=False)
			if self.modifications.value:
				embed.add_field(name="Modifications <:WarningSign:1041651261595975720>", value=self.modifications.value, inline=False)
			if self.bugfixes.value:
				embed.add_field(name="Bug Fixes <:Bug:1041649763625472030>", value=self.bugfixes.value, inline=False)
			embed.add_field(name="Download <:Download:1041649764929916938>", value=" https://github.com/Droptop-Four/Update/releases/tag/Update", inline=False)
			embed.set_footer(text="UserID: ( {} ) | sID: ( {} )".format(interaction.user.id, interaction.user.display_name), icon_url=interaction.user.avatar.url)
			await annchannel.send(f"New Droptop Version! {dtbrping.mention}")
			await annchannel.send(embed=embed, view=view)
			await interaction.followup.send(f"Version {self.version.value} of droptop was released", ephemeral=True)
		
		else:
			await interaction.response.send_message(f"Version `{self.version.value}` is not accettable", ephemeral=True)
	
	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message(f"Oops! Something went wrong.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)



class NewPoll(discord.ui.Modal, title="New Poll"):

	def __init__(self, emoji_1, emoji_2):
		super().__init__()
		self.emoji_1 = emoji_1
		self.emoji_2 = emoji_2

	poll_title = discord.ui.TextInput(
		label="Title",
		placeholder="Title here...",
	)

	description = discord.ui.TextInput(
		label="Description",
		style=discord.TextStyle.paragraph,
		placeholder="Description here...",
		required=False
	)

	async def on_submit(self, interaction: discord.Interaction):
		poll_role = discord.utils.get(interaction.guild.roles, id=configs["newversion_role"])
		await interaction.response.send_message("Sending poll...", ephemeral=True)
		if self.description.value:
			embed = discord.Embed(title=self.poll_title.value, description=self.description.value, color=discord.Color.from_rgb(75, 215, 100))
		else:
			embed = discord.Embed(title=self.poll_title.value, description="", color=discord.Color.from_rgb(75, 215, 100))
		embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
		await interaction.channel.send(f"New Droptop Announcement! {poll_role.mention}")
		embedsend = await interaction.channel.send(embed=embed)
		await embedsend.add_reaction(self.emoji_1)
		await embedsend.add_reaction(self.emoji_2)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message(f"Oops! Something went wrong.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)



class AdminCommands(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot


	@commands.Cog.listener()
	async def on_ready(self):
		self.member_stats.start()
		self.version_stats.start()

	
	@loop(seconds=600)
	async def member_stats(self):
		channel = self.bot.get_channel(self.bot.configs["memberstats_channel"])
		guild = self.bot.get_guild(self.bot.configs["server_id"])
		members = guild.member_count
		if str(members) in channel.name:
			pass
		else:
			await channel.edit(name = "Members: "+str(members))

	
	@loop(seconds=600)
	async def version_stats(self):
		channel = self.bot.get_channel(self.bot.configs["versionstats_channel"])
		version = github_reader("data/version.json")
		await channel.edit(name = "Droptop Version: "+str(version["version"]))


	@app_commands.command(name="new_version")
	async def new_version(self, interaction: discord.Interaction):
		"""Creates a new version of droptop."""

		await interaction.response.send_modal(NewVersion())
	
	
	@app_commands.command(name="reactrole")
	@app_commands.describe(
		emoji="The emoji you want people to react with",
		role="The role you want to add",
		message="The message you want to show on the embed"
	)
	@app_commands.default_permissions(manage_roles=True)
	async def reactrole(self, interaction: discord.Interaction, emoji: str, role: discord.Role, message: str):
		"""Creates a reactionrole in the channel"""
		
		if emoji not in ej.UNICODE_EMOJI["en"]:
			await interaction.response.send_message("You didn't set a supported emoji or no emoji at all.\nTry again using a UNICODE emoji (all the default ones supported by Discord).", ephemeral=True)
		else:
			emb = discord.Embed(description=message)
			await interaction.response.send_message(embed=emb)
			ogmsg = await interaction.original_message()
			await ogmsg.add_reaction(emoji)
			with open("reactrole.json") as json_file:
				data = json.load(json_file)
				new_react_role = {"role_name": role.name, "role_id": role.id, "emoji": emoji, "message_id": ogmsg.id, "message": message}
				data.append(new_react_role)
			with open("reactrole.json", "w") as f:
				json.dump(data, f, indent=4)


	@app_commands.command(name="poll")
	@app_commands.default_permissions(manage_nicknames=True)
	@app_commands.describe(
		emoji_1="The first emoji you want people to react with",
		emoji_2="The second emoji you want people to react with",
	)
	async def poll(self, interaction: discord.Interaction, emoji_1: str, emoji_2: str):
		"""Creates a poll"""

		await interaction.response.send_modal(NewPoll(emoji_1, emoji_2))




async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(AdminCommands(bot))
