
import discord
from discord import app_commands
from discord.ext import commands
import datetime

from typing import List, Optional


class ModerationCommands(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.report_message = app_commands.ContextMenu(
			name="Report Message to Moderators",
			callback=self.report_message,
		)
		self.report_member = app_commands.ContextMenu(
			name="Report Member to Moderators",
			callback=self.report_member,
		)
		self.bot.tree.add_command(self.report_message)
		self.bot.tree.add_command(self.report_member)
	
	
	async def report_message(self, interaction: discord.Interaction, message: discord.Message):
		await interaction.response.send_message(f"Thanks for reporting this message by {message.author.mention} to our moderators.", ephemeral=True)
		log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
		embed = discord.Embed(title="Reported Message", color=discord.Colour.from_rgb(213, 39, 62))
		if message.content:
			embed.description = message.content
		embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
		embed.timestamp = message.created_at
		url_view = discord.ui.View()
		url_view.add_item(discord.ui.Button(label="Go to Message", style=discord.ButtonStyle.url, url=message.jump_url))
		await log_channel.send(embed=embed, view=url_view)


	async def report_member(self, interaction: discord.Interaction, member: discord.Member):
		await interaction.response.send_message(f"Thanks for reporting {member.mention} to our moderators.", ephemeral=True)
		log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
		embed = discord.Embed(title="Reported Member", color=discord.Colour.from_rgb(213, 39, 62))
		embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
		embed.description = f"{member.mention} was reported by {interaction.user.mention}."
		await log_channel.send(embed=embed)


	
	@app_commands.command(name="kick")
	@app_commands.describe(
		member="The member you want to kick",
		reason="The reason for the kick"
	)
	@app_commands.default_permissions(manage_channels=True)
	async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
		"""Kicks a member from the server."""
		
		await interaction.guild.kick(member, reason=reason)
		log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
		embed = discord.Embed(title=f"Member kicked", description=f"{interaction.user.mention} kicked {member.mention}", color=discord.Colour.from_rgb(213, 39, 62))
		embed.add_field(name="Reason", value=reason)
		await log_channel.send(embed=embed)
		await interaction.response.send_message(f"{member.mention} successfully kicked.", ephemeral=True)

	
	@app_commands.command(name="ban")
	@app_commands.describe(
		member="The member you want to ban",
		reason="The reason for the ban"
	)
	@app_commands.default_permissions(manage_channels=True)
	async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
		"""Bans a member from the server."""

		await interaction.guild.ban(member, reason=reason)
		log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
		embed = discord.Embed(title=f"Member banned", description=f"{interaction.user.mention} banned {member.mention}", color=discord.Colour.from_rgb(213, 39, 62))
		embed.add_field(name="Reason", value=reason)
		await log_channel.send(embed=embed)
		await interaction.response.send_message(f"{member.mention} successfully banned.", ephemeral=True)


	async def banned_members_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		banned_users = []
		async for entry in interaction.guild.bans():
			banned_users.append(entry.user.name)
		return [
			app_commands.Choice(name=item, value=item)
			for item in banned_users if current.lower() in item.lower()
		]

	@app_commands.command(name="unban")
	@app_commands.describe(
		member="The member you want to unban",
		reason="The reason for the unban"
	)
	@app_commands.autocomplete(member=banned_members_autocomplete)
	@app_commands.default_permissions(manage_channels=True)
	async def unban(self, interaction: discord.Interaction, member: str, reason: Optional[str] = None):
		"""Unbans the specified member."""

		async for entry in interaction.guild.bans():
			if member.lower() == entry.user.name.lower():
				banned_user = entry.user.id
				banned_user = await self.bot.fetch_user(int(banned_user))
				await interaction.guild.unban(banned_user, reason=reason)
				log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
				embed = discord.Embed(title=f"Member unbanned", description=f"{interaction.user.mention} unbanned {banned_user.mention}", color=discord.Colour.from_rgb(213, 39, 62))
				embed.add_field(name="Reason", value=reason)
				await log_channel.send(embed=embed)
				await interaction.response.send_message(f"{banned_user.mention} successfully unbanned.", ephemeral=True)
			else:
				await interaction.response.send_message(f"{member} is not banned.")

	
	@app_commands.command(name="purge")
	@app_commands.describe(
		amount="The amount of messages you want to delete",
		reason="The reason for the purge"
	)
	@app_commands.default_permissions(manage_channels=True)
	async def purge(self, interaction: discord.Interaction, amount: Optional[int] = 15, reason: Optional[str] = None):
		"""Purge messages from the channel. Default is 15 messages."""
	
		await self.bot.wait_until_ready()
		await interaction.response.send_message(f"Starting to purge {interaction.channel.mention}...", ephemeral=True)
		await interaction.channel.purge(limit=amount)
		log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
		embed = discord.Embed(title=f"Channel Purged", description=f"{interaction.user.mention} purged {interaction.channel.mention}", color=discord.Colour.from_rgb(213, 39, 62))
		embed.add_field(name="Messages", value=amount)
		embed.add_field(name="Reason", value=reason)
		await log_channel.send(embed=embed)
		await interaction.followup.send(f"{interaction.channel.mention} successfully purged.", ephemeral=True)


	async def duration_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		duration_list = ["60 secs", "5 mins", "10 mins", "1 hour", "1 day", "1 week"]
		return [
			app_commands.Choice(name=item, value=item)
			for item in duration_list if current.lower() in item.lower()
		]

	@app_commands.command(name="timeout")
	@app_commands.describe(
		member="The member you want to timeout",
		duration="The duration of the timeout",
		reason="The reason for the timeout"
	)
	@app_commands.autocomplete(duration=duration_autocomplete)
	@app_commands.default_permissions(manage_channels=True)
	async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: Optional[str] = "60 secs", reason: Optional[str] = None):
		"""Timeout the specified member. Default is 60 seconds."""

		if duration in ["60 secs", "5 mins", "10 mins", "1 hour", "1 day", "1 week"]:
			if duration == "60 secs":
				delta = datetime.timedelta(seconds=60)
			elif duration == "5 mins":
				delta = datetime.timedelta(minutes=5)
			elif duration == "10 mins":
				delta = datetime.timedelta(minutes=10)
			elif duration == "1 hour":
				delta = datetime.timedelta(hours=1)
			elif duration == "1 day":
				delta = datetime.timedelta(days=1)
			else:
				delta = datetime.timedelta(days=7)
			await member.timeout(delta, reason=reason)
			log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
			embed = discord.Embed(title=f"Member timed out", description=f"{interaction.user.mention} timed out {member.mention}", color=discord.Colour.from_rgb(213, 39, 62))
			embed.add_field(name="Duration", value=f"{duration}")
			embed.add_field(name="Reason", value=reason)
			await log_channel.send(embed=embed)
			await interaction.response.send_message(f"{member.mention} successfully timed out.", ephemeral=True)
		else:
			await interaction.response.send_message(f"{duration} is not a valid duration.")
		
		


	@app_commands.command(name="timeout_remove")
	@app_commands.describe(
		member="The member you want to remove the timeout from",
		reason="The reason for the timeout remove"
	)
	@app_commands.default_permissions(manage_channels=True)
	async def timeout_remove(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
		"""Remove the timeout from the specified member."""

		if member.is_timed_out():
			await member.timeout(None, reason=reason)
			log_channel = interaction.guild.get_channel(self.bot.configs["moderationlog_channel"])
			embed = discord.Embed(title=f"Removed time out", description=f"{interaction.user.mention} removed the time out from {member.mention}", color=discord.Colour.from_rgb(213, 39, 62))
			embed.add_field(name="Reason", value=reason)
			await log_channel.send(embed=embed)
			await interaction.response.send_message(f"successfully removed the time out from {member.mention}.", ephemeral=True)
		else:
			await interaction.response.send_message(f"{member.mention} is not timed out.", ephemeral=True)



async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(ModerationCommands(bot))
	