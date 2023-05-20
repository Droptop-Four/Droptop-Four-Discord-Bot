import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.tasks import loop

from utils import github_reader, json_update, version_validator, sync_files

import traceback


class NewVersion(discord.ui.Modal, title="New Version"):
	def __init__(self, configs):
		super().__init__()
		self.configs = configs

		self.version = discord.ui.TextInput(
			label="Version",
			placeholder="Use only numbers and dots. ex '4.309'",
		)
	
		self.miniversion = discord.ui.TextInput(
			label="Mini Version",
			placeholder="Use only numbers. ex '58'",
		)
	
		self.features = discord.ui.TextInput(
			label="New Features",
			style=discord.TextStyle.paragraph,
			placeholder="Type new features here...",
			required=False,
		)
	
		self.modifications = discord.ui.TextInput(
			label="Modifications",
			style=discord.TextStyle.paragraph,
			placeholder="Type modifications here...",
			required=False,
		)
	
		self.bugfixes = discord.ui.TextInput(
			label="Bug Fixes",
			style=discord.TextStyle.paragraph,
			placeholder="Type bug fixes here...",
			required=False,
		)

		self.add_item(self.version)
		self.add_item(self.miniversion)
		self.add_item(self.features)
		self.add_item(self.modifications)
		self.add_item(self.bugfixes)

	async def on_submit(self, interaction: discord.Interaction):
		dtbrping = discord.utils.get(interaction.guild.roles, id=self.configs["newversion_role"])
		annchannel = interaction.guild.get_channel(self.configs["announcements_channel"])

		if version_validator(self.version.value):
			versiontuple = (self.version.value, self.miniversion.value)

			await interaction.response.send_message(f"Version {self.version.value} of droptop is being released", ephemeral=True)
			
			updated_json = json_update("version", version = versiontuple)
	
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url="https://github.com/Droptop-Four/Update/raw/main/Droptop%20Update.rmskin")
			view.add_item(item=download_button)
	
			embed = discord.Embed(title=f"📢 Droptop Four {self.version.value}.{self.miniversion.value}", url="https://github.com/Droptop-Four/Update/releases/tag/Update", color=0x2F3136)
			if self.features.value:
				embed.add_field(name="New features 🆕", value=self.features.value, inline=False)
			if self.modifications.value:
				embed.add_field(name="Modifications ⚠️", value=self.modifications.value, inline=False)
			if self.bugfixes.value:
				embed.add_field(name="Bug Fixes 🪲", value=self.bugfixes.value, inline=False)
			embed.add_field(name="Download", value="⬇️ Download:\nhttps://github.com/Droptop-Four/Update/releases/tag/Update", inline=False)
			embed.set_footer(text="UserID: ( {} ) | sID: ( {} )".format(interaction.user.id, interaction.user.display_name), icon_url=interaction.user.avatar.url)
			
			await annchannel.send(f"New Droptop Announcement! {dtbrping.mention}")
			await annchannel.send(embed=embed, view=view)
			await interaction.edit_original_response(content=f"Version {self.version.value}.{self.miniversion.value} of droptop was released")

			await interaction.followup.send("Syncing files on firebase...", ephemeral=True)

			files = ["https://github.com/Droptop-Four/Basic-Version/raw/main/Droptop%20Basic%20Version.rmskin", "https://github.com/Droptop-Four/Update/raw/main/Droptop%20Update.rmskin"]
			names = ["Droptop Basic Version.rmskin", "Droptop Update.rmskin"]
			bucket_url = self.configs["firebase_bucket_url"]
			webhook_url = self.configs["log_channel_webhook_url"]

			sync_files(files, names, bucket_url, webhook_url)

		else:
			await interaction.response.send_message(f"Version `{self.version.value}` is not accettable", ephemeral=True)
	
	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)


class NewPoll(discord.ui.Modal, title="New Poll"):

	def __init__(self, configs, emoji_1, emoji_2):
		super().__init__()
		self.configs = configs
		self.emoji_1 = emoji_1
		self.emoji_2 = emoji_2

		self.poll_title = discord.ui.TextInput(
			label="Title",
			placeholder="Title here...",
		)
	
		self.description = discord.ui.TextInput(
			label="Description",
			style=discord.TextStyle.paragraph,
			placeholder="Description here...",
			required=False
		)

		self.add_item(self.poll_title)
		self.add_item(self.description)

	async def on_submit(self, interaction: discord.Interaction):
		poll_role = discord.utils.get(interaction.guild.roles, id=self.configs["poll_role"])
		await interaction.response.send_message("Sending poll...", ephemeral=True)
		if self.description.value:
			embed = discord.Embed(title=self.poll_title.value, description=self.description.value, color=discord.Color.from_rgb(75, 215, 100))
		else:
			embed = discord.Embed(title=self.poll_title.value, description="", color=discord.Color.from_rgb(75, 215, 100))
		embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
		await interaction.channel.send(f"New Poll! {poll_role.mention}")
		embedsend = await interaction.channel.send(embed=embed)
		await embedsend.add_reaction(self.emoji_1)
		await embedsend.add_reaction(self.emoji_2)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong.\n{error}", ephemeral=True)
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
		version = github_reader(self.bot.configs["github_token"], "data/version.json")
		await channel.edit(name = "Droptop Version: "+str(version["version"]))


	@app_commands.command(name="new_version")
	async def new_version(self, interaction: discord.Interaction):
		"""Creates a new version of droptop."""

		await interaction.response.send_modal(NewVersion(self.bot.configs))


	@app_commands.command(name="poll")
	@app_commands.default_permissions(manage_nicknames=True)
	@app_commands.describe(
		emoji_1="The first emoji you want people to react with",
		emoji_2="The second emoji you want people to react with",
	)
	async def poll(self, interaction: discord.Interaction, emoji_1: str, emoji_2: str):
		"""Creates a poll"""

		await interaction.response.send_modal(NewPoll(self.bot.configs, emoji_1, emoji_2))

	
	@app_commands.command(name="sync_firebase")
	async def sync_firebase(self, interaction: discord.Interaction):
		"""Syncs firebase with github"""

		await interaction.response.send_message("Syncing files on firebase...", ephemeral=True)

		files = ["https://github.com/Droptop-Four/Basic-Version/raw/main/Droptop%20Basic%20Version.rmskin", "https://github.com/Droptop-Four/Update/raw/main/Droptop%20Update.rmskin"]
		names = ["Droptop Basic Version.rmskin", "Droptop Update.rmskin"]
		bucket_url = self.bot.configs["firebase_bucket_url"]
		webhook_url = self.bot.configs["log_channel_webhook_url"]

		sync_files(files, names, bucket_url, webhook_url)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(AdminCommands(bot))
