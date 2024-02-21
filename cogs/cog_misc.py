from datetime import datetime
from time import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class MiscCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.misc_ctx_menu = app_commands.ContextMenu(
            name="Show Join Date",
            callback=self.show_join_date,
        )
        self.bot.tree.add_command(self.misc_ctx_menu)

    async def show_join_date(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        await interaction.response.send_message(
            f"{member} joined at {discord.utils.format_dt(member.joined_at)}",
            ephemeral=True,
        )

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        """Returns the latency"""

        pingstart = time()
        await interaction.response.send_message(
            f"**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms."
        )
        pingend = time()
        await interaction.edit_original_response(
            content=f"**Pong!** The latency is: `{round(self.bot.latency * 1000)}`ms. The response time is: `{(pingend-pingstart)*1000:.0f}`ms."
        )

    @app_commands.command(name="uptime")
    async def uptime(self, interaction: discord.Interaction):
        """Returns the uptime of the bot"""

        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        embed = discord.Embed(
            title="Uptime", color=discord.Color.from_rgb(75, 215, 100)
        )
        embed.description = f"The bot has been on for:\n```css\n{days}d, {hours}h, {minutes}m, {seconds}s\n```"

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction):
        """Says hello!"""

        await interaction.response.send_message(
            f"Hi, {interaction.user.mention}! Thanks for greeting me!\nYou just earned a special role...😁\nCheck in your profile!",
            ephemeral=True,
        )
        role = discord.utils.get(
            self.bot.get_guild(interaction.guild_id).roles, id=817106505253388328
        )
        await interaction.user.add_roles(role)

    @app_commands.command(name="send")
    @app_commands.rename(text_to_send="text")
    @app_commands.describe(text_to_send="Text to send in the current channel")
    async def send(self, interaction: discord.Interaction, text_to_send: str):
        """Sends the text into the current channel."""

        await interaction.response.send_message(text_to_send)

    @app_commands.command(name="joined")
    @app_commands.describe(
        member="The member you want to get the joined date from; defaults to the user who uses the command"
    )
    async def joined(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Says when a member joined."""

        member = member or interaction.user
        await interaction.response.send_message(
            f"{member} joined {discord.utils.format_dt(member.joined_at)}",
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MiscCommands(bot))
