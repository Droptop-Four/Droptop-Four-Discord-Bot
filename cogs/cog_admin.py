import logging
import traceback
from typing import List

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.tasks import loop

from utils import (
    edit_release,
    get_version,
    github_reader,
    json_update,
    sync_files,
    validate_date,
    version_validator,
)

_logger = logging.getLogger(__name__)


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
        if len(self.features.value) > 1024:
            await interaction.response.send_message(
                "The features are too long", ephemeral=True
            )
            return

        if len(self.modifications.value) > 1024:
            await interaction.response.send_message(
                "The modifications are too long", ephemeral=True
            )
            return

        if len(self.bugfixes.value) > 1024:
            await interaction.response.send_message(
                "The bug fixes are too long", ephemeral=True
            )
            return

        dtbrping = discord.utils.get(
            interaction.guild.roles, id=self.configs["newversion_role"]
        )
        annchannel = interaction.guild.get_channel(
            self.configs["announcements_channel"]
        )

        if version_validator(self.version.value):
            versiontuple = (self.version.value, self.miniversion.value)

            await interaction.response.send_message(
                f"Version {self.version.value} of droptop is being released",
                ephemeral=True,
            )

            features = []
            if self.features.value != "":
                for r in self.features.value.split("\n"):
                    features.append(r.replace("- ", ""))
            modifications = []
            if self.modifications.value != "":
                for r in self.modifications.value.split("\n"):
                    modifications.append(r.replace("- ", ""))
            bugfixes = []
            if self.bugfixes.value != "":
                for r in self.bugfixes.value.split("\n"):
                    bugfixes.append(r.replace("- ", ""))

            updated_version_json = json_update(
                self.configs["github_private_key"], "version", version=versiontuple
            )
            updated_changelog_json = json_update(
                self.configs["github_private_key"],
                "changelog",
                version=versiontuple,
                cl_features=features,
                cl_modifications=modifications,
                cl_bugfixes=bugfixes,
            )

            view = discord.ui.View()
            style = discord.ButtonStyle.url
            download_button = discord.ui.Button(
                style=style,
                label="Download",
                url=f"https://github.com/Droptop-Four/Droptop-Four/releases/download/v{self.version.value}.{self.miniversion.value}/Droptop_Update.rmskin",
            )
            view.add_item(item=download_button)

            embed = discord.Embed(
                title=f"📢 Droptop Four {self.version.value}.{self.miniversion.value}",
                url=f"https://github.com/Droptop-Four/Droptop-Four/releases/tag/v{self.version.value}.{self.miniversion.value}",
                color=0x2F3136,
            )
            if self.features.value:
                embed.add_field(
                    name="<:New:1219373925062934689> New features",
                    value=self.features.value,
                    inline=False,
                )
            if self.modifications.value:
                embed.add_field(
                    name="<:Caution:1219373926791250000> Modifications",
                    value=self.modifications.value,
                    inline=False,
                )
            if self.bugfixes.value:
                embed.add_field(
                    name="<:Mosquito:1219373928867303535> Bug Fixes",
                    value=self.bugfixes.value,
                    inline=False,
                )
            embed.add_field(
                name="<:Download:1219374850494431283> Download",
                value=f"https://github.com/Droptop-Four/Droptop-Four/releases/download/v{self.version.value}.{self.miniversion.value}/Droptop_Update.rmskin",
                inline=False,
            )
            embed.set_footer(
                text="UserID: ( {} ) | sID: ( {} )".format(
                    interaction.user.id, interaction.user.display_name
                ),
                icon_url=interaction.user.avatar.url,
            )

            await annchannel.send(f"New Droptop Announcement! {dtbrping.mention}")
            await annchannel.send(embed=embed, view=view)
            await interaction.edit_original_response(
                content=f"Version {self.version.value}.{self.miniversion.value} of droptop was released"
            )

            edited = edit_release(
                self.configs["github_private_key"],
                versiontuple,
                features,
                modifications,
                bugfixes,
            )

            if not edited:
                await interaction.followup.send(
                    f"The release with the v{versiontuple[0]}.{versiontuple[1]} tag doesn't exists!!\nMake sure to publish the release first or to use a valid version!",
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                "Syncing files on firebase...", ephemeral=True
            )

            files = [
                "https://github.com/Droptop-Four/Droptop-Four/releases/latest/download/Droptop_Basic_Version.rmskin",
                "https://github.com/Droptop-Four/Droptop-Four/releases/latest/download/Droptop_Update.rmskin",
            ]
            names = ["Droptop Basic Version.rmskin", "Droptop Update.rmskin"]
            bucket_url = self.configs["firebase_bucket_url"]
            webhook_url = self.configs["log_channel_webhook_url"]

            sync_files(files, names, bucket_url, webhook_url)

        else:
            await interaction.response.send_message(
                f"Version `{self.version.value}` is not accettable", ephemeral=True
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        channel = interaction.guild.get_channel(bot.configs["commandlog_channel"])

        embed = discord.Embed(
            title="!!ERROR!!", color=discord.Color.from_rgb(255, 0, 0)
        )
        embed.add_field(name="User", value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(
            name="Channel", value=f"<#{interaction.channel_id}>", inline=False
        )
        embed.add_field(
            name="Command", value=f"{interaction.command.qualified_name}", inline=False
        )
        embed.add_field(
            name="Command mention",
            value=f"{interaction.command.extras['mention']}",
            inline=False,
        )
        embed.add_field(name="Error", value=error, inline=False)
        traceback_str = "".join(traceback.format_tb(error.__traceback__))
        embed.add_field(
            name="Traceback", value=f"```fix\n{traceback_str}\n```", inline=False
        )

        await channel.send(embed=embed)

        _logger.error(
            f"User: <@{interaction.user.id}>; Channel: <#{interaction.channel_id}>; Command: {interaction.command.qualified_name}; Error: {error}; Traceback: {traceback_str}"
        )

        await interaction.followup.send(
            f"Oops! Something went wrong.\n{error}", ephemeral=True
        )


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
            required=False,
        )

        self.add_item(self.poll_title)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        poll_role = discord.utils.get(
            interaction.guild.roles, id=self.configs["poll_role"]
        )
        await interaction.response.send_message("Sending poll...", ephemeral=True)
        if self.description.value:
            embed = discord.Embed(
                title=self.poll_title.value,
                description=self.description.value,
                color=discord.Color.from_rgb(75, 215, 100),
            )
        else:
            embed = discord.Embed(
                title=self.poll_title.value,
                description="",
                color=discord.Color.from_rgb(75, 215, 100),
            )
        embed.set_author(
            name=interaction.user.display_name, icon_url=interaction.user.display_avatar
        )
        await interaction.channel.send(f"New Poll! {poll_role.mention}")
        embedsend = await interaction.channel.send(embed=embed)
        await embedsend.add_reaction(self.emoji_1)
        await embedsend.add_reaction(self.emoji_2)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.followup.send(
            f"Oops! Something went wrong.\n{error}", ephemeral=True
        )

        channel = interaction.guild.get_channel(bot.configs["commandlog_channel"])

        embed = discord.Embed(
            title="!!ERROR!!", color=discord.Color.from_rgb(255, 0, 0)
        )
        embed.add_field(name="User", value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(
            name="Channel", value=f"<#{interaction.channel_id}>", inline=False
        )
        embed.add_field(
            name="Command", value=f"{interaction.command.qualified_name}", inline=False
        )
        embed.add_field(
            name="Command mention",
            value=f"{interaction.command.extras['mention']}",
            inline=False,
        )
        embed.add_field(name="Error", value=error, inline=False)
        traceback_str = "".join(traceback.format_tb(error.__traceback__))
        embed.add_field(
            name="Traceback", value=f"```fix\n{traceback_str}\n```", inline=False
        )

        await channel.send(embed=embed)

        _logger.error(
            f"User: <@{interaction.user.id}>; Channel: <#{interaction.channel_id}>; Command: {interaction.command.qualified_name}; Error: {error}; Traceback: {traceback_str}"
        )


class NewAnnouncement(discord.ui.Modal, title="New Announcement"):
    def __init__(self, configs, type, scope):
        super().__init__()
        self.configs = configs
        self.type = type.lower()
        self.scope = scope

        self.date = discord.ui.TextInput(
            label="Date", placeholder="dd/mm/yy", required=True
        )

        self.expiration = discord.ui.TextInput(
            label="Expiration", placeholder="dd/mm/yy", required=False
        )

        self.announcement = discord.ui.TextInput(
            label="Announcement", placeholder="Your announcement", required=True
        )

        self.add_item(self.date)
        self.add_item(self.expiration)
        self.add_item(self.announcement)

        async def on_submit(self, interaction: discord.Interaction):

            await interaction.response.send_message(
                "Creating new announcement", ephemeral=True
            )

            date_raw = self.date.value
            expiration_raw = self.expiration.value
            announcement_raw = self.announcement.value

            if validate_date(date_raw) and validate_date(expiration_raw):

                date_day = date_raw[:2]
                date_month = date_raw[3:5]
                date_year = date_raw[6:]

                date = date_year + "." + date_month + date_day

                if not expiration_raw:
                    expiration = "None"
                else:
                    expiration_day = expiration_raw[:2]
                    expiration_month = expiration_raw[3:5]
                    expiration_year = expiration_raw[6:]

                    expiration = (
                        expiration_year + "." + expiration_month + expiration_day
                    )

                announcement = announcement_raw

                json_update(
                    self.configs["github_private_key"],
                    "announcement",
                    ann_date=date,
                    ann_expiration=expiration,
                    announcement=announcement,
                    ann_type=self.type,
                    ann_scope=self.scope,
                )

                await interaction.edit_original_response(
                    content="New announcement created"
                )

            else:
                await interaction.followup.send(
                    "Invalid dates\nThe dates you entered are not formatted correctly: they should be in the `dd/mm/yy` format!",
                    ephemeral=True,
                )

        async def on_error(
            self, interaction: discord.Interaction, error: Exception
        ) -> None:
            await interaction.followup.send(
                f"Oops! Something went wrong, contact Bunz.\n{error}", ephemeral=True
            )

            channel = interaction.guild.get_channel(bot.configs["commandlog_channel"])

            embed = discord.Embed(
                title="!!ERROR!!", color=discord.Color.from_rgb(255, 0, 0)
            )
            embed.add_field(
                name="User", value=f"<@{interaction.user.id}>", inline=False
            )
            embed.add_field(
                name="Channel", value=f"<#{interaction.channel_id}>", inline=False
            )
            embed.add_field(
                name="Command",
                value=f"{interaction.command.qualified_name}",
                inline=False,
            )
            embed.add_field(
                name="Command mention",
                value=f"{interaction.command.extras['mention']}",
                inline=False,
            )
            embed.add_field(name="Error", value=error, inline=False)
            traceback_str = "".join(traceback.format_tb(error.__traceback__))
            embed.add_field(
                name="Traceback", value=f"```fix\n{traceback_str}\n```", inline=False
            )

            await channel.send(embed=embed)

            _logger.error(
                f"User: <@{interaction.user.id}>; Channel: <#{interaction.channel_id}>; Command: {interaction.command.qualified_name}; Error: {error}; Traceback: {traceback_str}"
            )


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.member_stats.start()
        self.version_stats.start()
        self.supporter_stats.start()

    @loop(seconds=600)
    async def member_stats(self):
        channel = self.bot.get_channel(self.bot.configs["memberstats_channel"])
        guild = self.bot.get_guild(self.bot.configs["server_id"])
        members = guild.member_count
        if str(members) in channel.name:
            pass
        else:
            await channel.edit(name="👥╏Members: " + str(members))

    @loop(seconds=600)
    async def version_stats(self):
        channel = self.bot.get_channel(self.bot.configs["versionstats_channel"])
        status, data = await get_version()
        if status == 200:
            await channel.edit(name="🆕╏Version: " + str(data["version"]))

    @loop(seconds=600)
    async def supporter_stats(self):
        channel = self.bot.get_channel(self.bot.configs["supporterstats_channel"])
        guild = self.bot.get_guild(self.bot.configs["server_id"])
        role = guild.get_role(self.bot.configs["supporter_role"])
        members = len(role.members)
        await channel.edit(name="💚╏Supporters: " + str(members))

    @app_commands.command(name="new_version")
    @app_commands.guild_only()
    async def new_version(self, interaction: discord.Interaction):
        """Creates a new version of droptop."""

        await interaction.response.send_modal(NewVersion(self.bot.configs))

    @app_commands.command(name="poll")
    @app_commands.default_permissions(manage_nicknames=True)
    @app_commands.describe(
        emoji_1="The first emoji you want people to react with",
        emoji_2="The second emoji you want people to react with",
    )
    @app_commands.guild_only()
    async def poll(self, interaction: discord.Interaction, emoji_1: str, emoji_2: str):
        """Creates a poll"""

        await interaction.response.send_modal(
            NewPoll(self.bot.configs, emoji_1, emoji_2)
        )

    @app_commands.command(name="sync_firebase")
    @app_commands.guild_only()
    async def sync_firebase(self, interaction: discord.Interaction):
        """Syncs firebase with github"""

        await interaction.response.send_message(
            "Syncing files on firebase...", ephemeral=True
        )

        files = [
            "https://github.com/Droptop-Four/Droptop-Four/releases/latest/download/Droptop_Basic_Version.rmskin",
            "https://github.com/Droptop-Four/Droptop-Four/releases/latest/download/Droptop_Update.rmskin",
        ]
        names = ["Droptop Basic Version.rmskin", "Droptop Update.rmskin"]
        bucket_url = self.bot.configs["firebase_bucket_url"]
        webhook_url = self.bot.configs["log_channel_webhook_url"]

        sync_files(files, names, bucket_url, webhook_url)

    async def type_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        types = ["Important", "Warning", "Info"]
        return [
            app_commands.Choice(name=type, value=type)
            for type in types
            if current.lower() in type.lower()
        ]

    async def scope_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        scopes = ["Website", "App", "Website & App"]
        return [
            app_commands.Choice(name=scope, value=scope)
            for scope in scopes
            if current.lower() in scope.lower()
        ]

    @app_commands.command(name="new-announcement")
    @app_commands.describe(type="Types", scope="Scopes")
    @app_commands.guild_only()
    @app_commands.autocomplete(type=type_autocomplete)
    @app_commands.autocomplete(scope=scope_autocomplete)
    async def new_announcement(
        self, interaction: discord.Interaction, type: str, scope: str
    ):
        """Creates a new announcement for the website/app"""

        await interaction.response.send_modal(
            NewAnnouncement(self.bot.configs, type, scope)
        )

    @app_commands.command(name="remove-announcement")
    @app_commands.describe(scope="Scopes")
    @app_commands.guild_only()
    @app_commands.autocomplete(scope=scope_autocomplete)
    async def remove_announcement(self, interaction: discord.Interaction, scope: str):
        """Removes an announcement on the website/app"""

        await interaction.response.send_message(
            "Removing the announcement...", ephemeral=True
        )
        json_update(
            self.bot.configs["github_private_key"],
            "announcement",
            ann_date=None,
            ann_expiration=None,
            announcement="",
            ann_type="",
            ann_scope=scope,
        )

        await interaction.edit_original_response(
            content=f"The announcement was removed for the {scope} scope!"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCommands(bot))
