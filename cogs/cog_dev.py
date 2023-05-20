import discord
from discord import app_commands
from discord.ext import commands

from typing import List


original_extensions = [
	"cogs.cog_admin",
	"cogs.cog_dev",
	"cogs.cog_mod",
	"cogs.cog_droptop",
	"cogs.cog_misc",
]


class DevCommands(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot


	async def cog_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		cogs_list = []
		extensions = original_extensions
		for extension in extensions:
			cogs_list.append(extension)
		return [
			app_commands.Choice(name=item, value=item)
			for item in cogs_list if current.lower() in item.lower()
		]

	
	@app_commands.command(name="reload_cog")
	@app_commands.describe(
		cog="The cog you want to reload"
	)
	@app_commands.autocomplete(cog=cog_autocomplete)
	async def reload_cog(self, interaction: discord.Interaction, cog: str):
		"""Reloads a cog."""

		cogs_list = []
		extensions = original_extensions
		for extension in extensions:
			cogs_list.append(extension)
		
		if cog not in cogs_list:
			return await interaction.response.send_message(f"The `{cog}` cog doesn't exist.", ephemeral=True)
		else:
			await interaction.response.send_message("Reloading cog...", ephemeral=True)
			await self.bot.unload_extension(cog)
			await self.bot.load_extension(cog)
			self.bot.tree.clear_commands(guild=self.bot.get_guild(self.bot.configs["server_id"]))
			await self.bot.tree.sync()
			await interaction.followup.send(f"`{cog}` successfully reloaded.", ephemeral=True)
			log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
			embed = discord.Embed(title="Reloaded Cog", description=f"{interaction.user.mention} reloaded the `{cog}` cog", color=discord.Colour.from_rgb(213, 39, 62))
			await log_channel.send(embed=embed)


	@app_commands.command(name="unload_cog")
	@app_commands.describe(
		cog="The cog you want to unload"
	)
	@app_commands.autocomplete(cog=cog_autocomplete)
	async def unload_cog(self, interaction: discord.Interaction, cog: str):
		"""Unloads a cog."""

		cogs_list = []
		extensions = original_extensions
		for extension in extensions:
			cogs_list.append(extension)
		
		if cog not in cogs_list:
			return await interaction.response.send_message(f"The `{cog}` cog doesn't exist.", ephemeral=True)
		else:
			await interaction.response.send_message("Unloading cog...", ephemeral=True)
			await self.bot.unload_extension(cog)
			self.bot.tree.clear_commands(guild=self.bot.get_guild(self.bot.configs["server_id"]))
			await self.bot.tree.sync()
			await interaction.followup.send(f"`{cog}` successfully unloaded.", ephemeral=True)
			log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
			embed = discord.Embed(title="Unloaded Cog", description=f"{interaction.user.mention} unloaded the `{cog}` cog", color=discord.Colour.from_rgb(213, 39, 62))
			await log_channel.send(embed=embed)

	
	@app_commands.command(name="load_cog")
	@app_commands.describe(
		cog="The cog you want to load"
	)
	@app_commands.autocomplete(cog=cog_autocomplete)
	async def load_cog(self, interaction: discord.Interaction, cog: str):
		"""Loads a cog."""

		cogs_list = []
		extensions = original_extensions
		for extension in extensions:
			cogs_list.append(extension)
		
		if cog not in cogs_list:
			return await interaction.response.send_message(f"The `{cog}` cog doesn't exist.", ephemeral=True)
		else:
			await interaction.response.send_message("Loading cog...", ephemeral=True)
			await self.bot.load_extension(cog)
			self.bot.tree.clear_commands(guild=self.bot.get_guild(self.bot.configs["server_id"]))
			await self.bot.tree.sync()
			await interaction.followup.send(f"`{cog}` successfully loaded.", ephemeral=True)
			log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
			embed = discord.Embed(title="Loaded Cog", description=f"{interaction.user.mention} loaded the `{cog}` cog", color=discord.Colour.from_rgb(213, 39, 62))
			await log_channel.send(embed=embed)


	@app_commands.command(name="list_cogs")
	async def list_cogs(self, interaction: discord.Interaction):
		"""Lists all loaded cogs."""

		string = "```css\n"
		string += "\n".join([str(cog) for cog in self.bot.extensions])
		string += "\n```"
		await interaction.response.send_message(string, ephemeral=True)


	@app_commands.command(name="sync_commands")
	async def sync_commands(self, interaction: discord.Interaction):
		"""Syncs the bot's commands."""

		await interaction.response.send_message("Syncing command tree...", ephemeral=True)
		self.bot.tree.clear_commands(guild=self.bot.get_guild(self.bot.configs["server_id"]))
		await self.bot.tree.sync()
		await interaction.followup.send("Command tree synced.", ephemeral=True)
		log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
		embed = discord.Embed(title="Synced Commands", description=f"{interaction.user.mention} synced the commands", color=discord.Colour.from_rgb(213, 39, 62))
		await log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DevCommands(bot))
