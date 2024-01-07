import discord
from discord import app_commands
from discord.ext import commands

from utils import github_reader, push_rmskin, push_image, img_rename, rmskin_name_check, rmskin_rename, to_webp, json_update, get_title_author, json_edit, json_delete, rmskin_delete, image_delete, version_date, get_releases_downloads, get_all_sales, get_metadata, get_stars, get_followers, initialize_crowdin

from typing import Optional, List
from pathlib import Path
import traceback, math, json, zipfile, configparser, os


class DroptopCommands(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot


	@app_commands.command(name="stats")
	async def stats(self, interaction: discord.Interaction) -> None:
		""" Displays stats about Droptop Four """

		embed = discord.Embed(color=discord.Color.from_rgb(75, 215, 100))
		embed.add_field(name="Loading...", value="Loading all the stats...")
		embed.set_author(name="Stats", icon_url="https://cdn-icons-png.flaticon.com/512/2881/2881355.png")

		await interaction.response.send_message(embed=embed)

		message = await interaction.original_response()

		gumroad_sales = get_all_sales(json.loads(self.bot.configs["gumroad_token"]))
		github_basic_downloads, github_update_downloads = get_releases_downloads(self.bot.configs["github_private_key"])
		deviantart_views, deviantart_favourites, deviantart_downloads = get_metadata(self.bot.configs["deviantart_auth_url"])
		github_followers = get_followers(self.bot.configs["github_private_key"])
		github_stars = get_stars(self.bot.configs["github_private_key"])
	
		embed.add_field(name="<:Download:1041649764929916938> Downloads", value=f"```css\nBasic Variant     {github_basic_downloads+deviantart_downloads}\nUpdate            {github_update_downloads}\nSupporter         {gumroad_sales}```", inline=False)
		embed.add_field(name="<:deviantart:1151924474548068482> DeviantArt", value=f"```css\nViews             {deviantart_views}\nFavourites        {deviantart_favourites}```", inline=False)
		embed.add_field(name="<:github:1152028987523076266> Github", value=f"```css\nFollowers         {github_followers}\nStars             {github_stars}```", inline=False)
	
		embed.remove_field(0)
	
		await message.edit(embeds=[embed])
	
	
	@app_commands.command(name="translation_status")
	async def translation_status(self, interaction: discord.Interaction):
		""" Displays infos about the translationsof Droptop """

		translation_platform_url = "https://translate.droptopfour.com"

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		button_b = discord.ui.Button(style=style, label="Translation platform", url=translation_platform_url)
		view.add_item(item=button_b)

		embed = discord.Embed(title="Translations Status", color=discord.Color.from_rgb(75, 215, 100))
		embed.add_field(name="Loading...", value="Loading the translation status...")
		embed.set_author(name="Go to the translation platform", url=translation_platform_url, icon_url="https://support.crowdin.com/assets/logos/small-scale-logo/png/smallscale-logo-cWhite.png")

		await interaction.response.send_message(embed=embed, view=view)

		client = initialize_crowdin(self.bot.configs["crowdin_token"])
		
		result = client.translation_status.get_project_progress(self.bot.configs["crowdin_project"], limit=100)["data"]

		embed.remove_field(0)

		embed2 = discord.Embed(color=discord.Color.from_rgb(75, 215, 100))

		i = 0
		for language in result:
			if i < 24:
				i = i + 1
				language_id = language["data"]["languageId"]
				language_name = client.languages.get_language(language_id)["data"]["name"]
				translation_status = language["data"]["translationProgress"]
				approval_status = language["data"]["approvalProgress"]
	
				translation_value = math.trunc(translation_status / 20)
				approval_value = math.trunc(approval_status / 20)
				
				if translation_value >= approval_value:
					remaining_value = (5 - translation_value)
				else:
					remaining_value = (5 - approval_value)
				
				if translation_value == 5:
					global_status = "✅"
				else:
					global_status = "❌"
	
				approvals = approval_value * ":green_square:"
				translated = (translation_value - approval_value) * ":blue_square:"
				black = remaining_value * "⬛"

				value=f"{approvals}{translated}{black}"
				embed.add_field(name=f"{i}: {language_name} {global_status}", value=value, inline=True)
				
			else:
				i = i + 1
				
				language_id = language["data"]["languageId"]
				language_name = client.languages.get_language(language_id)["data"]["name"]
				translation_status = language["data"]["translationProgress"]
				approval_status = language["data"]["approvalProgress"]
	
				translation_value = math.trunc(translation_status / 20)
				approval_value = math.trunc(approval_status / 20)

				if translation_value >= approval_value:
					remaining_value = (5 - translation_value)
				else:
					remaining_value = (5 - approval_value)
				
				if translation_value == 5:
					global_status = "✅"
				else:
					global_status = "❌"
				
				approvals = approval_value * ":green_square:"
				translated = (translation_value - approval_value) * ":blue_square:"
				black = remaining_value * "⬛"
				
				value=f"{approvals}{translated}{black}"
				embed2.add_field(name=f"{i}: {language_name} {global_status}", value=value, inline=True)

		embed2.set_footer(text=f"Droptop currently has partial or complete support for {i} languages.")
		
		message = await interaction.original_response()
		await message.edit(embeds=[embed, embed2])


	droptop_group = app_commands.Group(name="droptop_four", description="Droptop Four command")

	
	async def variant_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		variants = ["Basic", "Supporter"]
		return [
			app_commands.Choice(name=variant, value=variant)
			for variant in variants if current.lower() in variant.lower()
		]

	
	@droptop_group.command(name="info")
	@app_commands.describe(
		variant="The Droptop Four variant you want info about"
	)
	@app_commands.autocomplete(variant=variant_autocomplete)
	async def droptop_four_info(self, interaction: discord.Interaction, variant: Optional[str] = None) -> None:
		""" Displays info about Droptop Four """
		
		data = github_reader(self.bot.configs["github_private_key"], "data/droptop_info.json")
		version = github_reader(self.bot.configs["github_private_key"], "data/version.json")

		if variant:
			if variant == "Basic":
				embed = discord.Embed(title="Droptop Four - Basic Variant", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
				embed.set_thumbnail(url=self.bot.droptopfour_logo)
				for field in data["messages"][0]["content"][1]["fields"]:
					embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
				embed.set_footer(text=data["messages"][0]["content"][1]["footer"])
				await interaction.response.send_message(embed=embed)
			
			elif variant == "Supporter":
				embed = discord.Embed(title="Droptop Four - Supporter Variant", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
				embed.set_thumbnail(url=self.bot.droptopfour_logo)
				for field in data["messages"][0]["content"][2]["fields"]:
					embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
				embed.set_footer(text=data["messages"][0]["content"][2]["footer"])
				await interaction.response.send_message(embed=embed)
			else:
				await interaction.response.send_message(f"The {variant} variant doesn't exists.", ephemeral=True)
		else:
			embed = discord.Embed(title="Droptop Four", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
			embed.set_thumbnail(url=self.bot.droptopfour_logo)
			for field in data["messages"][0]["content"][0]["fields"]:
				embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
			embed.add_field(name="Latest Version", value=version["version"], inline=False)
			embed.set_footer(text=data["messages"][0]["content"][0]["footer"])
			await interaction.response.send_message(embed=embed)


	@app_commands.command(name="download")
	@app_commands.describe(
		variant="The Droptop Four variant you want download info about"
	)
	@app_commands.autocomplete(variant=variant_autocomplete)
	async def download(self, interaction: discord.Interaction, variant: Optional[str] = None):
		"""Displays downloads info about Droptop Four"""

		data = github_reader(self.bot.configs["github_private_key"], "data/droptop_info.json")

		if variant:
			if variant == "Basic":
				view = discord.ui.View()
				style = discord.ButtonStyle.url
				button_b = discord.ui.Button(style=style, label="Download Basic", url="https://github.com/Droptop-Four/Droptop-Four/releases/latest/download/Droptop_Basic_Version.rmskin")
				view.add_item(item=button_b)
				embed = discord.Embed(title="Droptop Four", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
				embed.set_thumbnail(url=self.bot.droptopfour_logo)
				for field in data["messages"][1]["content"][1]["fields"]:
					embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
				embed.set_footer(text=data["messages"][1]["content"][1]["footer"])
				await interaction.response.send_message(embed=embed, view=view)
			
			elif variant == "Supporter":
				view = discord.ui.View()
				style = discord.ButtonStyle.url
				button_s = discord.ui.Button(style=style, label="Download Supporter", url="https://gumroad.com/l/droptop")
				view.add_item(item=button_s)
				embed = discord.Embed(title="Droptop Four", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
				embed.set_thumbnail(url=self.bot.droptopfour_logo)
				for field in data["messages"][1]["content"][2]["fields"]:
					embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
				embed.set_footer(text=data["messages"][1]["content"][2]["footer"])
				await interaction.response.send_message(embed=embed, view=view)
			else:
				await interaction.response.send_message(f"The {variant} variant doesn't exists.", ephemeral=True)
		else:
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			button_b = discord.ui.Button(style=style, label="Download Basic", url="https://github.com/Droptop-Four/Droptop-Four/releases/latest/download/Droptop_Basic_Version.rmskin")
			button_s = discord.ui.Button(style=style, label="Download Supporter", url="https://gumroad.com/l/droptop")
			view.add_item(item=button_b)
			view.add_item(item=button_s)
			embed = discord.Embed(title="Droptop Four", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
			embed.set_thumbnail(url=self.bot.droptopfour_logo)
			for field in data["messages"][1]["content"][0]["fields"]:
				embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
			embed.set_footer(text=data["messages"][1]["content"][0]["footer"])
			await interaction.response.send_message(embed=embed, view=view)


	@app_commands.command(name="solved")
	async def solved(self, interaction: discord.Interaction):
		"""Adds the solved tag to help-bug report forum channel"""

		if interaction.channel.parent.id == self.bot.configs["help_bug_report_channel"]:
			await interaction.response.send_message("This thread was set as closed")
			await interaction.channel.add_tags(discord.Object(self.bot.configs["solved_forum_tag"]))
			await interaction.channel.remove_tags(discord.Object(self.bot.configs["unsolved_forum_tag"]))
			await interaction.channel.edit(archived=True)

		else:
			await interaction.response.send_message("You can use this command only in the help thread", ephemeral=True)

	
	@app_commands.command(name="update")
	async def update(self, interaction: discord.Interaction):
		"""Displays update info about Droptop Four"""

		data = github_reader(self.bot.configs["github_private_key"], "data/droptop_info.json")

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		button = discord.ui.Button(style=style, label="Download Update", url="https://github.com/Droptop-Four/Droptop-Four/releases/latest/download/Droptop_Update.rmskin")
		view.add_item(item=button)

		embed = discord.Embed(title="Droptop Four Update", color=discord.Color.from_rgb(75, 215, 100))
		embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
		embed.set_thumbnail(url=self.bot.droptopfour_logo)
		for field in data["messages"][2]["content"][0]["fields"]:
			embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
		embed.set_footer(text=data["messages"][2]["content"][0]["footer"])
		await interaction.response.send_message(embed=embed, view=view)


	@app_commands.command(name="faq")
	async def faq(self, interaction: discord.Interaction):
		"""Displays the F.A.Q. link"""

		data = github_reader(self.bot.configs["github_private_key"], "data/droptop_info.json")

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		button = discord.ui.Button(style=style, label="FAQs", url="https://droptopfour.com/faq")
		view.add_item(item=button)

		embed = discord.Embed(title="Droptop Four F.A.Q.", color=discord.Color.from_rgb(75, 215, 100))
		for field in data["messages"][3]["content"][0]["fields"]:
			embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
		await interaction.response.send_message(embed=embed, view=view)

	
	@app_commands.command(name="website")
	async def website(self, interaction: discord.Interaction):
		"""Displays the website link"""

		data = github_reader(self.bot.configs["github_private_key"], "data/droptop_info.json")

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		button = discord.ui.Button(style=style, label="Website", url="https://droptopfour.com")
		view.add_item(item=button)

		embed = discord.Embed(title="Droptop Four website", color=discord.Color.from_rgb(75, 215, 100))
		for field in data["messages"][4]["content"][0]["fields"]:
			embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
		await interaction.response.send_message(embed=embed, view=view)


	async def delete_channel_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		list = ["True", "False"]
		return [
			app_commands.Choice(name=item, value=item)
			for item in list if current.lower() in item.lower()
		]
	

	community_app_group = app_commands.Group(name="community_app", description="Community apps commands")

	
	async def community_apps_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		community_apps_names = []
		data = github_reader(self.bot.configs["github_private_key"], "data/community_apps/community_apps.json")
		for app in data["apps"]:
			community_apps_names.append(app["app"]["name"])
		return [
			app_commands.Choice(name=community_app_name, value=community_app_name)
			for community_app_name in community_apps_names if current.lower() in community_app_name.lower()
		][:25]

	
	async def authorised_community_app_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		community_apps_editable = []
		data = github_reader(self.bot.configs["github_private_key"], "data/community_apps/community_apps.json")
		for app in data["apps"]:
			if interaction.user.id in app["app"]["authorised_members"]:
				community_apps_editable.append(f'{app["app"]["name"]} - {app["app"]["author"]}')
		return [
			app_commands.Choice(name=community_app_name, value=community_app_name)
			for community_app_name in community_apps_editable if current.lower() in community_app_name.lower()
		][:25]


	@community_app_group.command(name="info")
	@app_commands.describe(
		name="The name of the community app you want info about (Only 25 elements are shown in the auto-completition list)"
	)
	@app_commands.autocomplete(name=community_apps_autocomplete)
	async def community_apps_info(self, interaction: discord.Interaction, name: str) -> None:
		""" Displays info about Droptop Four Community Apps  """

		data = github_reader(self.bot.configs["github_private_key"], "data/community_apps/community_apps.json")

		community_apps_names = []
		for app in data["apps"]:
			community_apps_names.append(app["app"]["name"])

		if name in community_apps_names:
			for app in data["apps"]:
				app = app["app"]
				if name.lower() == app["name"].lower():
					id = app["id"]
					name = app["name"]
					author = app["author"]
					description = app["desc"]
					version = app["version"]
					download_link = app["direct_download_link"]
					image_url = app["image_url"]
	
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url=download_link)
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptopfour.com/community-apps?id={id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
	
			embed = discord.Embed(title=f"{name} - {author}", description=f"{description}", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="Community App Info", url=self.bot.configs["website"]+"/community-apps")
			embed.add_field(name="Version: ", value=version, inline=False)
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)
			embed.set_image(url=image_url)
			await interaction.response.send_message(embed=embed, view=view)

		else:
			await interaction.response.send_message(f"The {name} community app doesn't exists.", ephemeral=True)
		
	
	@community_app_group.command(name="new_release")
	@app_commands.describe(
		rmskin_package="The package of your Community App"
	)
	async def community_app_new_release(self, interaction: discord.Interaction, rmskin_package: discord.Attachment):
		"""Creates a new Community App Release to Github, the website and the discord server."""
		
		channel = self.bot.get_channel(self.bot.configs["appreleases_channel"])

		await interaction.response.send_message("Checking if the package is valid...", ephemeral=True)

		if rmskin_name_check("app", rmskin_package.filename):
			rmskin_name = rmskin_rename("app", rmskin_package.filename)
			rmskin_path = Path(f"tmp/{rmskin_name}")
			await rmskin_package.save(rmskin_path)

			with zipfile.ZipFile(rmskin_path, "r") as rmskin_archive:
				ini_path = Path("tmp/RMSKIN.ini")
				rmskin_archive.extract("RMSKIN.ini", "tmp")
				config = configparser.ConfigParser()
				config.read(ini_path)
				app_title = config['rmskin']['Name']
				author = config['rmskin']['Author']
				version = config['rmskin']['Version']
				try: 
					UUID = config['rmskin']['GUID']
				except:
					await interaction.followup.send("No UUID was found inside your rmskin package!\nBe sure to update droptop and repackage your app.", ephemeral=True)
					return

				ini_path.unlink()

				preview_image = f"Skins\Droptop Community Apps\Apps\{app_title.replace(' ', '_')}-{author.replace(' ', '_')}\Images\PreviewImage.png"
				if preview_image in rmskin_archive.namelist():
					pass
				else:
					await interaction.followup.send("No image preview was found inside your rmskin package!\nBe sure to insert an image during the packaging process and repackage your app.", ephemeral=True)
					return

			data = github_reader(self.bot.configs["github_private_key"], "data/community_apps/community_apps.json")
			for app in data["apps"]:
				if UUID == app["app"]["uuid"]:
					new = False
					default_description = app["app"]["desc"]
					default_github_profile = app["app"]["author_link"]
					default_github_repo = app["app"]["official_link"]
					break
				else:
					new = True
					default_description = ""
					default_github_profile = ""
					default_github_repo = ""

			async def confirm_callback(interaction):
				await interaction.response.send_modal(NewAppRelease(self.bot.configs, rmskin_path, rmskin_name, channel, new, default_description, default_github_profile, default_github_repo))

			async def cancel_callback(interaction):
				await interaction.response.send_message("Action cancelled...", ephemeral=True)

			confirm_button = discord.ui.Button(label="Confirm" , style=discord.ButtonStyle.green)
			cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
			confirm_button.callback = confirm_callback
			cancel_button.callback = cancel_callback
			view = discord.ui.View()
			view.add_item(confirm_button)
			view.add_item(cancel_button)
			original = await interaction.original_response()
			await original.edit(content=f"Your package is fine!\nDo you want to continue with the release of the **{app_title}** by **{author}** *(v{version})*?", view=view)

		else:
			await interaction.response.send_message("No rmskin app package was found, be sure to put it in the right hitbox the next time.", ephemeral=True)

	
	@community_app_group.command(name="edit")
	@app_commands.describe(
		image_preview="The image of your Community App",
		authorised_member_1="A member you want to authorise to make changes to your app",
		authorised_member_2="A member you want to authorise to make changes to your app"
	)
	@app_commands.autocomplete(community_app=authorised_community_app_autocomplete)
	async def community_app_edit(self, interaction: discord.Interaction, community_app: str, image_preview: discord.Attachment = None, authorised_member_1: Optional[discord.Member] = None, authorised_member_2: Optional[discord.Member] = None):
		"""Edits a Community App Release."""

		channel = self.bot.get_channel(self.bot.configs["appreleases_channel"])
		authorised_members = []

		if authorised_member_1:
			authorised_members.append(authorised_member_1)
		if authorised_member_2:
			authorised_members.append(authorised_member_2)
		
		if image_preview:
			if image_preview.filename.lower().endswith((".jpg", ".jpeg", ".png")):
				await interaction.response.send_modal(EditAppRelease(self.bot.configs, community_app, channel, image_preview=image_preview, suffix="jpg", authorised_members=authorised_members))	
			elif image_preview.filename.lower().endswith(".webp"):
				await interaction.response.send_modal(EditAppRelease(self.bot.configs, community_app, channel, image_preview=image_preview, suffix="webp", authorised_members=authorised_members))
			else:
				await interaction.response.send_message("No image was found, be sure to put it in the right hitbox the next time.", ephemeral=True)
		else:
			await interaction.response.send_modal(EditAppRelease(self.bot.configs, community_app, channel, authorised_members=authorised_members))


	@community_app_group.command(name="delete")
	@app_commands.describe(
		community_app = "The name of the community app you can delete",
		delete_release_channel = "If to delete the release channel (default yes)"
	)
	@app_commands.autocomplete(community_app=authorised_community_app_autocomplete, delete_release_channel=delete_channel_autocomplete)
	async def community_app_delete(self, interaction: discord.Interaction, community_app: str, delete_release_channel: Optional[str] = "True"):
		"""Deletes a Community App Release."""

		view = ConfirmDeletion(community_app)
		await interaction.response.send_message(f"Are you sure you want to permanently delete:\n```diff\n- {community_app}\n```\n*(This action is irreversible)*", ephemeral=True, view=view)
		await view.wait()
		if view.value is None:
			await interaction.followup.send("You took to long to reply, and the command expired.", ephemeral=True)
		elif view.value:
			data = github_reader(self.bot.configs["github_private_key"], "data/community_apps/community_apps.json")
			for app in data["apps"]:
				if community_app == f'{app["app"]["name"]} - {app["app"]["author"]}':
					uuid = app["app"]["uuid"]
			json_delete(self.bot.configs["github_private_key"], "app", uuid)
			rmskin_delete(self.bot.configs["github_private_key"], "app", community_app)
			image_delete(self.bot.configs["github_private_key"], "app", community_app)
			if delete_release_channel == "True":
				channel = self.bot.get_channel(self.bot.configs["appreleases_channel"])
				threads = []
				for thread in channel.threads:
					threads.append(thread)
		
				async for thread in channel.archived_threads():
					threads.append(thread)
				
				if community_app in threads:
					await thread.delete()
					await interaction.followup.send(f"The {community_app} app was succesfully deleted.\nAlso the post in <#{channel.id}> was deleted", ephemeral=True)
				else:
					await interaction.followup.send(f"The {community_app} app was succesfully deleted.", ephemeral=True)
			else:
				await interaction.followup.send(f"The {community_app} app was succesfully deleted.", ephemeral=True)
		else:
			pass


	community_theme_group = app_commands.Group(name="community_theme", description="Community themes commands")


	async def community_themes_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		community_themes_names = []
		data = github_reader(self.bot.configs["github_private_key"], "data/community_themes/community_themes.json")
		for theme in data["themes"]:
			community_themes_names.append(theme["theme"]["name"])
		return [
			app_commands.Choice(name=community_theme_name, value=community_theme_name)
			for community_theme_name in community_themes_names if current.lower() in community_theme_name.lower()
		][:25]


	async def authorised_community_theme_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		community_themes_editable = []
		data = github_reader(self.bot.configs["github_private_key"], "data/community_themes/community_themes.json")
		for theme in data["themes"]:
			if interaction.user.id in theme["theme"]["authorised_members"]:
				community_themes_editable.append(f'{theme["theme"]["name"]} - {theme["theme"]["author"]}')
		return [
			app_commands.Choice(name=community_theme_name, value=community_theme_name)
			for community_theme_name in community_themes_editable if current.lower() in community_theme_name.lower()
		][:25]


	@community_theme_group.command(name="info")
	@app_commands.describe(
		name="The name of the community theme you want info about (Only 25 elements are shown in the auto-completition list)"
	)
	@app_commands.autocomplete(name=community_themes_autocomplete)
	async def community_theme_info(self, interaction: discord.Interaction, name: str) -> None:
		"""Displays info about Droptop Four Community Themes"""

		data = github_reader(self.bot.configs["github_private_key"], "data/community_themes/community_themes.json")

		community_themes_names = []
		for theme in data["themes"]:
			community_themes_names.append(theme["theme"]["name"])

		if name in community_themes_names:
			for theme in data["themes"]:
				theme = theme["theme"]
				if name.lower() == theme["name"].lower():
					id = theme["id"]
					name = theme["name"]
					author = theme["author"]
					description = theme["desc"]
					download_link = theme["direct_download_link"]
					image_url = theme["image_url"]
	
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url=download_link)
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptopfour.com/community-themes/?id={id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
	
			embed = discord.Embed(title=f"{name} - {author}", description=f"{description}", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="Community Theme Info", url=self.bot.configs["website"]+"/community-themes")
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)
			embed.set_image(url=image_url)
			await interaction.response.send_message(embed=embed, view=view)
			
		else:
			await interaction.response.send_message(f"The {name} community theme doesn't exists.", ephemeral=True)


	@community_theme_group.command(name="new_release")
	@app_commands.describe(
		rmskin_package="The package of your Community Theme",
		image_preview="The image of your Community Theme"
	)
	async def community_theme_new_release(self, interaction: discord.Interaction, rmskin_package: discord.Attachment, image_preview: discord.Attachment):
		"""Creates a new Community Theme Release to Github, the website and the discord server."""
		
		channel = self.bot.get_channel(self.bot.configs["themereleases_channel"])

		if rmskin_name_check("theme", rmskin_package.filename):
			
			title, author = get_title_author("theme", rmskin_package.filename)

			community_json = github_reader(self.bot.configs["github_private_key"], "data/community_themes/community_themes.json")

			available = True
			for theme in community_json["themes"]:
				theme_tags = theme["theme"]
				if theme_tags["name"] == title:
					if interaction.user.id in theme_tags["authorised_members"]:
						available = True
					else:
						available = False

			if available:
				if image_preview.filename.lower().endswith((".jpg", ".jpeg", ".png")):
					await interaction.response.send_modal(NewThemeRelease(self.bot.configs, title, author, "jpg", rmskin_package, image_preview, channel))
				elif image_preview.filename.lower().endswith(".webp"):
					await interaction.response.send_modal(NewThemeRelease(self.bot.configs, title, author, "webp", rmskin_package, image_preview, channel))
				else:
					await interaction.response.send_message("No image was found, be sure to put it in the right hitbox the next time.", ephemeral=True)
			else:
				await interaction.response.send_message("The name you chose is not available, choose another one for your theme", ephemeral=True)
		else:
			await interaction.response.send_message("No rmskin theme package was found, be sure to put it in the right hitbox the next time.", ephemeral=True)


	@community_theme_group.command(name="edit")
	@app_commands.describe(
		image_preview="The image of your Community Theme",
		authorised_member_1="A member you want to authorise to make changes to your theme",
		authorised_member_2="A member you want to authorise to make changes to your theme"
	)
	@app_commands.autocomplete(community_theme=authorised_community_theme_autocomplete)
	async def community_theme_edit(self, interaction: discord.Interaction, community_theme: str, image_preview: discord.Attachment = None, authorised_member_1: Optional[discord.Member] = None, authorised_member_2: Optional[discord.Member] = None):
		"""Edits a Community Theme Release."""

		channel = self.bot.get_channel(self.bot.configs["themereleases_channel"])
		authorised_members = []

		if authorised_member_1:
			authorised_members.append(authorised_member_1)
		if authorised_member_2:
			authorised_members.append(authorised_member_2)
		
		if image_preview:
			if image_preview.filename.lower().endswith((".jpg", ".jpeg", ".png")):
				await interaction.response.send_modal(EditThemeRelease(self.bot.configs, community_theme, channel, image_preview=image_preview, suffix="jpg", authorised_members=authorised_members))	
			elif image_preview.filename.lower().endswith(".webp"):
				await interaction.response.send_modal(EditThemeRelease(self.bot.configs, community_theme, channel, image_preview=image_preview, suffix="webp", authorised_members=authorised_members))
			else:
				await interaction.response.send_message("No image was found, be sure to put it in the right hitbox the next time.", ephemeral=True)
		else:
			await interaction.response.send_modal(EditThemeRelease(self.bot.configs, community_theme, channel, authorised_members=authorised_members))


	@community_theme_group.command(name="delete")
	@app_commands.describe(
		community_theme = "The name of the community theme you can delete",
		delete_release_channel = "If to delete the release channel"
	)
	@app_commands.autocomplete(community_theme=authorised_community_theme_autocomplete, delete_release_channel=delete_channel_autocomplete)
	async def community_theme_delete(self, interaction: discord.Interaction, community_theme: str, delete_release_channel: Optional[str] = "True"):
		"""Deletes a Community Theme Release."""

		view = ConfirmDeletion(community_theme)
		await interaction.response.send_message(f"Are you sure you want to permanently delete:\n```diff\n- {community_theme}\n```\n*(This action is irreversible)*", ephemeral=True, view=view)
		await view.wait()
		if view.value is None:
			await interaction.followup.send("You took to long to reply, and the command expired.", ephemeral=True)
		elif view.value:
			data = github_reader(self.bot.configs["github_private_key"], "data/community_themes/community_themes.json")
			for theme in data["themes"]:
				if community_theme == f'{theme["theme"]["name"]} - {theme["theme"]["author"]}':
					uuid = theme["theme"]["uuid"]
			json_delete(self.bot.configs["github_private_key"], "theme", uuid)
			rmskin_delete(self.bot.configs["github_private_key"], "theme", community_theme)
			image_delete(self.bot.configs["github_private_key"], "theme", community_theme)
			if delete_release_channel == "True":
				channel = self.bot.get_channel(self.bot.configs["themereleases_channel"])
				threads = []
				for thread in channel.threads:
					threads.append(thread)
		
				async for thread in channel.archived_threads():
					threads.append(thread)
				
				if community_theme in threads:
					await thread.delete()
					await interaction.followup.send(f"The {community_theme} theme was succesfully deleted.\nAlso the post in <#{channel.id}> was deleted", ephemeral=True)
				else:
					await interaction.followup.send(f"The {community_theme} theme was succesfully deleted.", ephemeral=True)
			else:
				await interaction.followup.send(f"The {community_theme} theme was succesfully deleted.", ephemeral=True)
		else:
			pass


class NewAppRelease(discord.ui.Modal, title="New App Release"):
	def __init__(self, configs, rmskin_path, rmskin_name, channel, new, default_description, default_github_profile, default_github_repo):
		super().__init__()
		self.configs = configs
		self.rmskin_path = rmskin_path
		self.rmskin_name = rmskin_name
		self.channel = channel
		self.new = new
		self.default_description = default_description
		self.default_github_profile = default_github_profile
		self.default_github_repo = default_github_repo
	
		self.description = discord.ui.TextInput(
			label="Description",
			style=discord.TextStyle.paragraph,
			placeholder="Description here...",
			default=self.default_description
		)

		self.changenotes = discord.ui.TextInput(
			label="Changenotes",
			style=discord.TextStyle.paragraph,
			placeholder="Changenotes here..."
		)

		self.github_profile = discord.ui.TextInput(
			label="Github Profile",
			placeholder="https://github.com/your-nickname",
			default=self.default_github_profile,
			required=False
		)
	
		self.github_repo = discord.ui.TextInput(
			label="Github Repository",
			placeholder="https://github.com/your-nickname/your-app-repo",
			default=self.default_github_repo,
			required=False
		)

		self.add_item(self.description)
		self.add_item(self.changenotes)
		self.add_item(self.github_profile)
		self.add_item(self.github_repo)

	async def on_submit(self, interaction: discord.Interaction):

		await interaction.response.send_message("Your app is being released... Please wait...", ephemeral=True)
		original = await interaction.original_response()
		community_json = github_reader(self.configs["github_private_key"], "data/community_apps/community_apps.json")
		authorised_members = []

		with zipfile.ZipFile(self.rmskin_path, "r") as rmskin_archive:
			ini_path = Path("tmp/RMSKIN.ini")
			rmskin_archive.extract("RMSKIN.ini", "tmp")
			config = configparser.ConfigParser()
			config.read(ini_path)
			app_title = config['rmskin']['Name']
			author = config['rmskin']['Author']
			version = config['rmskin']['Version']
			UUID = config['rmskin']['GUID']

			ini_path.unlink()
				
			preview_image = f"Skins\Droptop Community Apps\Apps\{app_title.replace(' ', '_')}-{author.replace(' ', '_')}\Images\PreviewImage.png"
			image_name = f"{app_title.replace(' ', '_')}-{author.replace(' ', '_')}"
			image_path = Path(f"tmp/{image_name}.png")
			rmskin_archive.extract(preview_image, "tmp")
			os.rename(f"tmp/{preview_image}", image_path)
			webp_path = to_webp(image_path)

		for item in community_json["apps"]:
			app_tags = item["app"]
			if app_tags["uuid"] == UUID:
				for member in app_tags["authorised_members"]:
					authorised_members.append(member)

		if self.new:
			authorised_members = [self.configs["author_id"], self.configs["cari_id"], interaction.user.id]
		
		if interaction.user.id in authorised_members:
			rmskin_creation = push_rmskin(self.configs["github_private_key"], "app", self.rmskin_name)
			image_creation = push_image(self.configs["github_private_key"], "app", image_name)
			updated_json, download_link, image_link, app_id, uuid = json_update(self.configs["github_private_key"], "app", authorised_members=authorised_members, title=app_title, author=author, description=self.description.value, changenotes= self.changenotes.value, rmskin_name=self.rmskin_name, image_name=image_name, version=version, uuid=UUID, author_link=self.github_profile.value, github_repo=self.github_repo.value)

			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url=download_link)
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptopfour.com/community-apps?id={app_id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
			embed = discord.Embed(title=f"{app_title} - {author}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="New Community App Release", url=self.configs["website"]+"/community-apps")
			embed.add_field(name="Version: ", value=version, inline=False)
			embed.add_field(name="Changenotes:", value=self.changenotes.value, inline=False)
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | uuid: ( {UUID} )", icon_url=interaction.user.avatar.url)
			embed.set_image(url=image_link)
			all_threads = []
			for thread in self.channel.threads:
				all_threads.append(thread)

			async for thread in self.channel.archived_threads():
				all_threads.append(thread)

			for thread in all_threads:
				if thread.name == f"{app_title} - {author}":
					await thread.send(embed=embed, view=view)
					break
			else:
				await self.channel.create_thread(name=f"{app_title} - {author}", embed=embed, view=view)

			webp_path.unlink()
			await original.edit(content=f"You successfully published **{app_title}** in <#{self.channel.id}>")
			self.rmskin_path.unlink()

		else:
			await interaction.response.send_message(f"You aren't authorised to publish updates, modify or delete {app_title}.\nAsk {author} to add you as an authorised user.", ephemeral=True)
			
	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong, contact Bunz.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)


class NewThemeRelease(discord.ui.Modal, title="New Theme Release"):
	def __init__(self, configs, theme_title, author, image_mode, rmskin_package, image_preview, channel):
		super().__init__()
		self.theme_title = theme_title
		self.author = author
		self.configs = configs
		self.image_mode = image_mode
		self.rmskin_package = rmskin_package
		self.image_preview = image_preview
		self.channel = channel

		data = github_reader(self.configs["github_private_key"], "data/community_themes/community_themes.json")
		for theme in data["themes"]:
			if self.theme_title == theme["theme"]["name"]:
				self.uuid = theme["theme"]["uuid"]
				self.default_description = theme["theme"]["desc"]
				self.default_github_profile = theme["theme"]["author_link"]
				self.default_github_repo = theme["theme"]["official_link"]
				break
			else:
				self.uuid = ""
				self.default_description = ""
				self.default_github_profile = ""
				self.default_github_repo = ""

		self.description = discord.ui.TextInput(
			label="Description",
			style=discord.TextStyle.paragraph,
			placeholder="Description here...",
			default=self.default_description,
			required=False
		)
		
		self.changenotes = discord.ui.TextInput(
			label="Changenotes",
			style=discord.TextStyle.paragraph,
			placeholder="Changenotes here...",
			required=False
		)
		
		self.github_profile = discord.ui.TextInput(
			label="Github Profile",
			placeholder="https://github.com/your-nickname",
			default=self.default_github_profile,
			required=False
		)
	
		self.github_repo = discord.ui.TextInput(
			label="Github Repository",
			placeholder="https://github.com/your-nickname/your-app-repo",
			default=self.default_github_repo,
			required=False
		)

		self.add_item(self.description)
		self.add_item(self.changenotes)
		self.add_item(self.github_profile)
		self.add_item(self.github_repo)

	async def on_submit(self, interaction: discord.Interaction):

		community_json = github_reader(self.configs["github_private_key"], "data/community_themes/community_themes.json")

		authorised_members = []

		version = version_date()

		for item in community_json["themes"]:
			theme_tags = item["theme"]
			if theme_tags["name"] == self.theme_title:
				for member in theme_tags["authorised_members"]:
					authorised_members.append(member)
				new = False
			else:
				new = True
		if new:
			authorised_members = [self.configs["author_id"], self.configs["cari_id"], interaction.user.id]
		
		if interaction.user.id in authorised_members:
			if self.image_mode == "jpg":
				await interaction.response.send_message("Your theme is being released... Please wait...", ephemeral=True)
				
				rmskin_name = rmskin_rename("theme", self.rmskin_package.filename)
				package_path = Path(f"tmp/{rmskin_name}")
				await self.rmskin_package.save(package_path)
				rmskin_creation = push_rmskin(self.configs["github_private_key"], "theme", rmskin_name)
				
				image_extension = Path(self.image_preview.filename).suffix
				image_name = img_rename("theme", self.rmskin_package.filename)
				image_path = Path(f"tmp/{image_name}{image_extension}")
				await self.image_preview.save(image_path)
				webp_path = to_webp(image_path)
				image_creation = push_image(self.configs["github_private_key"], "theme", image_name)
				
				updated_json, download_link, image_link, theme_id, uuid = json_update(self.configs["github_private_key"], "theme", authorised_members=authorised_members, title=self.theme_title, author=self.author, description=self.description.value, changenotes=self.changenotes.value, rmskin_name=rmskin_name, image_name=image_name, version=version, author_link=self.github_profile.value, github_repo=self.github_repo.value)
				
				view = discord.ui.View()
				style = discord.ButtonStyle.url
				download_button = discord.ui.Button(style=style, label="Download", url=download_link)
				site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptopfour.com/community-themes?id={theme_id}")
				view.add_item(item=download_button)
				view.add_item(item=site_button)
				if self.description.value:
					embed = discord.Embed(title=f"{self.theme_title} - {self.author}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
				else:
					embed = discord.Embed(title=f"{self.theme_title} - {self.author}", description="", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="New Community Theme Release", url=self.configs["website"]+"/community-themes")
				embed.add_field(name="Changenotes:", value=self.changenotes.value, inline=False)
				embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | uuid: ( {uuid} )", icon_url=interaction.user.avatar.url)
				image_file = await self.image_preview.to_file(filename="image.png")
				embed.set_image(url="attachment://image.png")
				threads = []

				for thread in self.channel.threads:
					threads.append(thread)
		
				async for thread in self.channel.archived_threads():
					threads.append(thread)
		
				for thread in threads:
					if thread.name == f"{self.theme_title} - {self.author}":
						await thread.send(embed=embed, file=image_file, view=view)
						break
				else:
					await self.channel.create_thread(name=f"{self.theme_title} - {self.author}", embed=embed, file=image_file, view=view)
				webp_path.unlink()
				await interaction.followup.send(f"You successfully published **{self.theme_title}** in <#{self.channel.id}>", ephemeral=True)
			else:
				await interaction.response.send_message("Your theme is being released... Please wait...", ephemeral=True)
				
				rmskin_name = rmskin_rename("theme", self.rmskin_package.filename)
				package_path = Path(f"tmp/{rmskin_name}")
				await self.rmskin_package.save(package_path)
				rmskin_creation = push_rmskin(self.configs["github_private_key"], "theme", rmskin_name)
				
				image_name = img_rename("theme", self.rmskin_package.filename)
				webp_path = Path(f"tmp/{image_name}.webp")
				await self.image_preview.save(webp_path)
				image_creation = push_image(self.configs["github_private_key"], "theme", image_name)
				
				updated_json, download_link, image_link, theme_id, uuid = json_update(self.configs["github_private_key"], "theme", authorised_members=authorised_members, title=self.theme_title, author=self.author, description=self.description.value, changenotes=self.changenotes.value, rmskin_name=rmskin_name, image_name=image_name, version=version, author_link=self.github_profile.value, github_repo=self.github_repo.value)
				
				view = discord.ui.View()
				style = discord.ButtonStyle.url
				download_button = discord.ui.Button(style=style, label="Download", url=download_link)
				site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptopfour.com/community-themes?id={theme_id}")
				view.add_item(item=download_button)
				view.add_item(item=site_button)
				if self.description.value:
					embed = discord.Embed(title=f"{self.theme_title} - {self.author}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
				else:
					embed = discord.Embed(title=f"{self.theme_title} - {self.author}", description="", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="New Community Theme Release", url=self.configs["website"]+"/community-themes")
				embed.add_field(name="Changenotes:", value=self.changenotes.value, inline=False)
				embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | uuid: ( {uuid} )", icon_url=interaction.user.avatar.url)
				image_file = await self.image_preview.to_file(filename="image.png")
				embed.set_image(url="attachment://image.png")
				threads = []

				for thread in self.channel.threads:
					threads.append(thread)
		
				async for thread in self.channel.archived_threads():
					threads.append(thread)
		
				for thread in threads:
					if thread.name == f"{self.theme_title} - {self.author}":
						await thread.send(embed=embed, file=image_file, view=view)
						break
				else:
					await self.channel.create_thread(name=f"{self.theme_title} - {self.author}", embed=embed, file=image_file, view=view)
				webp_path.unlink()
				await interaction.followup.send(f"You successfully published **{self.theme_title}** in <#{self.channel.id}>", ephemeral=True)
			package_path.unlink()
		else:
			await interaction.followup.send(f"You aren't authorised to publish updates, modify or delete {self.theme_title}.\nAsk {self.author} to add you as an authorised user.", ephemeral=True)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong, contact Bunz.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)


class EditAppRelease(discord.ui.Modal, title="Edit App Release"):
	def __init__(self, configs, community_app, channel, *, image_preview=None, suffix=None, authorised_members=None):
		super().__init__()
		self.configs = configs
		self.community_app = community_app
		self.channel = channel
		self.image_preview = image_preview
		self.suffix = suffix
		self.authorised_members = authorised_members

		data = github_reader(self.configs["github_private_key"], "data/community_apps/community_apps.json")
		for app in data["apps"]:
			if self.community_app == f'{app["app"]["name"]} - {app["app"]["author"]}':
				self.uuid = app["app"]["uuid"]
				self.default_name = app["app"]["name"]
				self.default_author = app["app"]["author"]
				self.version = app["app"]["version"]
				self.default_description = app["app"]["desc"]
				self.default_github_profile = app["app"]["author_link"]
				self.default_github_repo = app["app"]["official_link"]
				self.image_url = app["app"]["image_url"]
				
		self.author = discord.ui.TextInput(
			label="Author",
			placeholder="Author here...",
			default=self.default_author,
			required=False
		)
	
		self.description = discord.ui.TextInput(
			label="Description",
			style=discord.TextStyle.paragraph,
			placeholder="Description here...",
			default=self.default_description,
			required=False
		)
		
		self.github_profile = discord.ui.TextInput(
			label="Github Profile",
			placeholder="https://github.com/your-nickname",
			default=self.default_github_profile,
			required=False
		)
	
		self.github_repo = discord.ui.TextInput(
			label="Github Repository",
			placeholder="https://github.com/your-nickname/your-app-repo",
			default=self.default_github_repo,
			required=False
		)

		self.add_item(self.author)
		self.add_item(self.description)
		self.add_item(self.github_profile)
		self.add_item(self.github_repo)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.send_message("Your app is being edited... Please wait...", ephemeral=True)

		if self.image_preview:
			if self.suffix == "jpg":
				image_extension = Path(self.image_preview.filename).suffix
				image_name = self.image_url.replace("https://raw.githubusercontent.com/Droptop-Four/test/main/data/community_apps/img/", "")
				image_name = image_name.replace(".webp", "")
				image_path = Path(f"tmp/{image_name}{image_extension}")
				await self.image_preview.save(image_path)
				webp_path = to_webp(image_path)
			else:
				image_name = self.image_url.replace("https://raw.githubusercontent.com/Droptop-Four/test/main/data/community_apps/img/", "")
				image_name = image_name.replace(".webp", "")
				webp_path = Path(f"tmp/{image_name}.webp")
				await self.image_preview.save(webp_path)
			
			image_creation = push_image(self.configs["github_private_key"], "app", image_name)

		updated_json, download_link, image_link, app_id = json_edit(self.configs["github_private_key"], "app", self.uuid, author=self.author.value, description=self.description.value, author_link=self.github_profile.value, github_repo=self.github_repo.value, authorised_members=self.authorised_members)

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		download_button = discord.ui.Button(style=style, label="Download", url=download_link)
		site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptopfour.com/community-apps?id={app_id}")
		view.add_item(item=download_button)
		view.add_item(item=site_button)
		embed = discord.Embed(title=f"{self.community_app}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
		embed.set_author(name="New Community App Release", url=self.configs["website"]+"/community-apps")
		embed.add_field(name="Version: ", value=self.version, inline=False)
		embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | uuid: ( {self.uuid} )", icon_url=interaction.user.avatar.url)
		if self.image_preview:
			image_file = await self.image_preview.to_file(filename="image.png")
			embed.set_image(url="attachment://image.png")
		else:
			embed.set_image(url=self.image_url)
		threads = []
		for thread in self.channel.threads:
			threads.append(thread)

		async for thread in self.channel.archived_threads():
			threads.append(thread)
		
		if f"{self.community_app}" in threads:
			if self.image_preview:
				await thread.send(embed=embed, file=image_file, view=view)

				messages = [message async for message in thread.history(limit=1, oldest_first=True)]

				newembed = discord.Embed(title=f"{self.community_app}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
				newembed.set_author(name="New Community App Release", url=self.configs["website"]+"/community-apps")
				newembed.set_footer(text=f"UserID: ( {interaction.user.id} ) | uuid: ( {self.uuid} )", icon_url=interaction.user.avatar.url)
				if self.image_preview:
					image_file = await self.image_preview.to_file(filename="image.png")
					newembed.set_image(url="attachment://image.png")
				else:
					newembed.set_image(url=self.image_url)
				
				await messages[0].edit(embed=newembed, attachments=[image_file], view=view)
			else:
				await thread.send(embed=embed, view=view)

				messages = [message async for message in thread.history(limit=1, oldest_first=True)]

				await messages[0].edit(embed=embed, view=view)
		else:
			if self.image_preview:
				await self.channel.create_thread(name=f"{self.community_app}", embed=embed, file=image_file, view=view)
			else:
				await self.channel.create_thread(name=f"{self.community_app}", embed=embed, view=view)
		if self.image_preview:
			webp_path.unlink()
		await interaction.followup.send(f"You successfully published **{self.community_app}** in <#{self.channel.id}>", ephemeral=True)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong, contact Bunz.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)


class EditThemeRelease(discord.ui.Modal, title="Edit Theme Release"):
	def __init__(self, configs, community_theme, channel, *, image_preview=None, suffix=None, authorised_members=None):
		super().__init__()
		self.configs = configs
		self.community_theme = community_theme
		self.channel = channel
		self.image_preview = image_preview
		self.suffix = suffix
		self.authorised_members = authorised_members

		data = github_reader(self.configs["github_private_key"], "data/community_themes/community_themes.json")
		for theme in data["themes"]:
			if self.community_theme == f'{theme["theme"]["name"]} - {theme["theme"]["author"]}':
				self.uuid = theme["theme"]["uuid"]
				self.default_name = theme["theme"]["name"]
				self.default_author = theme["theme"]["author"]
				self.default_description = theme["theme"]["desc"]
				self.default_github_profile = theme["theme"]["author_link"]
				self.default_github_repo = theme["theme"]["official_link"]
				self.image_url = theme["theme"]["image_url"]
				
		self.author = discord.ui.TextInput(
			label="Author",
			placeholder="Author here...",
			default=self.default_author,
			required=False
		)
	
		self.description = discord.ui.TextInput(
			label="Description",
			style=discord.TextStyle.paragraph,
			placeholder="Description here...",
			default=self.default_description,
			required=False
		)
		
		self.github_profile = discord.ui.TextInput(
			label="Github Profile",
			placeholder="https://github.com/your-nickname",
			default=self.default_github_profile,
			required=False
		)
	
		self.github_repo = discord.ui.TextInput(
			label="Github Repository",
			placeholder="https://github.com/your-nickname/your-theme-repo",
			default=self.default_github_repo,
			required=False
		)

		self.add_item(self.author)
		self.add_item(self.description)
		self.add_item(self.github_profile)
		self.add_item(self.github_repo)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.send_message("Your theme is being edited... Please wait...", ephemeral=True)

		if self.image_preview:
			if self.suffix == "jpg":
				image_extension = Path(self.image_preview.filename).suffix
				image_name = self.image_url.replace("https://raw.githubusercontent.com/Droptop-Four/test/main/data/community_themes/img/", "")
				image_name = image_name.replace(".webp", "")
				image_path = Path(f"tmp/{image_name}{image_extension}")
				await self.image_preview.save(image_path)
				webp_path = to_webp(image_path)
			else:
				image_name = self.image_url.replace("https://raw.githubusercontent.com/Droptop-Four/test/main/data/community_themes/img/", "")
				image_name = image_name.replace(".webp", "")
				webp_path = Path(f"tmp/{image_name}.webp")
				await self.image_preview.save(webp_path)
				
			image_creation = push_image(self.configs["github_private_key"], "theme", image_name)

		updated_json, download_link, image_link, theme_id = json_edit(self.configs["github_private_key"], "theme", self.uuid, author=self.author.value, description=self.description.value, author_link=self.github_profile.value, github_repo=self.github_repo.value, authorised_members=self.authorised_members)

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		download_button = discord.ui.Button(style=style, label="Download", url=download_link)
		site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptopfour.com/community-themes?id={theme_id}")
		view.add_item(item=download_button)
		view.add_item(item=site_button)
		embed = discord.Embed(title=f"{self.community_theme}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
		embed.set_author(name="New Community Theme Release", url=self.configs["website"]+"/community-themes")
		embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | uuid: ( {self.uuid} )", icon_url=interaction.user.avatar.url)
		if self.image_preview:
			image_file = await self.image_preview.to_file(filename="image.png")
			embed.set_image(url="attachment://image.png")
		else:
			embed.set_image(url=self.image_url)
		threads = []
		for thread in self.channel.threads:
			threads.append(thread)

		async for thread in self.channel.archived_threads():
			threads.append(thread)
		
		if f"{self.community_theme}" in threads:
			if self.image_preview:
				await thread.send(embed=embed, file=image_file, view=view)

				messages = [message async for message in thread.history(limit=1, oldest_first=True)]

				newembed = discord.Embed(title=f"{self.community_theme}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
				newembed.set_author(name="New Community Theme Release", url=self.configs["website"]+"/community-themes")
				newembed.set_footer(text=f"UserID: ( {interaction.user.id} ) | uuid: ( {self.uuid} )", icon_url=interaction.user.avatar.url)
				if self.image_preview:
					image_file = await self.image_preview.to_file(filename="image.png")
					newembed.set_image(url="attachment://image.png")
				else:
					newembed.set_image(url=self.image_url)
				
				await messages[0].edit(embed=newembed, attachments=[image_file], view=view)
			else:
				await thread.send(embed=embed, view=view)

				messages = [message async for message in thread.history(limit=1, oldest_first=True)]

				await messages[0].edit(embed=embed, view=view)
		else:
			if self.image_preview:
				await self.channel.create_thread(name=f"{self.community_theme}", embed=embed, file=image_file, view=view)
			else:
				await self.channel.create_thread(name=f"{self.community_theme}", embed=embed, view=view)
		if self.image_preview:
			webp_path.unlink()
		await interaction.followup.send(f"You successfully published **{self.community_theme}** in <#{self.channel.id}>", ephemeral=True)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong, contact Bunz.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)


class ConfirmDeletion(discord.ui.View):
	def __init__(self, community_app):
		super().__init__()
		self.community_app = community_app
		self.value = None


	@discord.ui.button(label='Confirm', style=discord.ButtonStyle.red)
	async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.value = True
		await interaction.response.send_message(f"The `{self.community_app}` package is being deleted...", ephemeral=True)
		self.stop()


	@discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.value = False
		await interaction.response.send_message(f"The `{self.community_app}` package **will NOT** be deleted.", ephemeral=True)
		self.stop()


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DroptopCommands(bot))
