import discord
from discord import app_commands
from discord.ext import commands

from utils import github_reader, push_rmskin, push_image, img_rename, rmskin_rename, to_webp, update_json

from typing import Optional, List
import traceback

from pathlib import Path


class NewAppRelease(discord.ui.Modal, title="New App Release"):

	def __init__(self, configs, image_mode, rmskin_package, image_preview, channel):
		super().__init__()
		self.configs = configs
		self.image_mode = image_mode
		self.rmskin_package = rmskin_package
		self.image_preview = image_preview
		self.channel = channel

	app_title = discord.ui.TextInput(
		label="Title",
		placeholder="Title here...",
	)
	
	author = discord.ui.TextInput(
		label="Author",
		placeholder="Author here...",
	)

	version = discord.ui.TextInput(
		label="Version",
		placeholder="Version here...",
	)

	description = discord.ui.TextInput(
		label="Description",
		style=discord.TextStyle.paragraph,
		placeholder="Description here...",
	)

	async def on_submit(self, interaction: discord.Interaction):
		
		if self.image_mode == "jpg":
			await interaction.response.send_message(f"Your app is being released... Please wait...", ephemeral=True)
			rmskin_name = rmskin_rename("app", self.app_title.value, self.author.value)
			package_path = Path(f"tmp/{rmskin_name}.rmskin")
			await self.rmskin_package.save(package_path)
			rmskin_creation = push_rmskin("app", self.app_title.value, self.author.value, rmskin_name, self.version.value)
			image_extension = Path(self.image_preview.filename).suffix
			image_name = img_rename(self.app_title.value, self.author.value)
			image_path = Path(f"tmp/{image_name}{image_extension}")
			await self.image_preview.save(image_path)
			webp_path = to_webp(image_path)
			image_creation = push_image("app", self.app_title.value, self.author.value, image_name, self.version.value)
			updated_json, download_link, image_link, app_id = update_json("app", self.app_title.value, self.author.value, self.description.value, rmskin_name, image_name, self.version.value)
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url=download_link)
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptop-four.github.io/community-apps#{app_id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
			embed = discord.Embed(title=f"{self.app_title.value} - {self.author.value}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="New Community App Release", url=self.configs["website"]+"/community-apps")
			embed.add_field(name="Version: ", value=self.version.value, inline=False)
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)
			image_file = await self.image_preview.to_file(filename="image.png")
			embed.set_image(url="attachment://image.png")
			threads = []
			for thread in self.channel.threads:
				threads.append(thread.name)
			if f"{self.app_title.value} - {self.author.value}" in threads:
				for thread in self.channel.threads:
					if f"{self.app_title.value} - {self.author.value}" in thread.name:
						same_thread = thread
				await same_thread.send(embed=embed, file=image_file, view=view)
			else:
				await self.channel.create_thread(name=f"{self.app_title.value} - {self.author.value}", embed=embed, file=image_file, view=view)
			webp_path.unlink()
			await interaction.followup.send(f"You successfully published **{self.app_title.value}** in <#{self.channel.id}>", ephemeral=True)

		else:
			await interaction.response.send_message(f"Your app is being released... Please wait...", ephemeral=True)
			rmskin_name = rmskin_rename("app", self.app_title.value, self.author.value)
			package_path = Path(f"tmp/{rmskin_name}.rmskin")
			await self.rmskin_package.save(package_path)
			rmskin_creation = push_rmskin("app", self.app_title.value, self.author.value, rmskin_name, self.version.value)
			image_name = img_rename(self.app_title.value, self.author.value)
			webp_path = Path(f"tmp/{image_name}.webp")
			await self.image_preview.save(webp_path)
			image_creation = push_image("app", self.app_title.value, self.author.value, image_name, self.version.value)
			updated_json, download_link, image_link, app_id = update_json("app", self.app_title.value, self.author.value, self.description.value, rmskin_name, image_name, self.version.value)
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url=download_link)
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptop-four.github.io/community-apps#{app_id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
			embed = discord.Embed(title=f"{self.app_title.value} - {self.author.value}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="New Community App Release", url=self.configs["website"]+"/community-apps")
			embed.add_field(name="Version: ", value=self.version.value, inline=False)
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)
			image_file = await self.image_preview.to_file(filename="image.png")
			embed.set_image(url="attachment://image.png")
			threads = []
			for thread in self.channel.threads:
				threads.append(thread.name)
			if f"{self.app_title.value} - {self.author.value}" in threads:
				for thread in self.channel.threads:
					if f"{self.app_title.value} - {self.author.value}" in thread.name:
						same_thread = thread
				await same_thread.send(embed=embed, file=image_file, view=view)
			else:
				await self.channel.create_thread(name=f"{self.app_title.value} - {self.author.value}", embed=embed, file=image_file, view=view)		
			webp_path.unlink()
			await interaction.followup.send(f"You successfully published **{self.app_title.value}** in <#{self.channel.id}>", ephemeral=True)
		package_path.unlink()

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)


class NewThemeRelease(discord.ui.Modal, title="New Theme Release"):

	def __init__(self, configs, image_mode, rmskin_package, image_preview, channel):
		super().__init__()
		self.configs = configs
		self.image_mode = image_mode
		self.rmskin_package = rmskin_package
		self.image_preview = image_preview
		self.channel = channel

	theme_title = discord.ui.TextInput(
		label="Title",
		placeholder="Title here...",
	)
	
	author = discord.ui.TextInput(
		label="Author",
		placeholder="Author here...",
	)

	description = discord.ui.TextInput(
		label="Description",
		style=discord.TextStyle.paragraph,
		placeholder="Description here...",
		required=False
	)

	async def on_submit(self, interaction: discord.Interaction):
		if self.image_mode == "jpg":
			await interaction.response.send_message(f"Your theme is being released... Please wait...", ephemeral=True)
			rmskin_name = rmskin_rename("theme", self.theme_title.value, self.author.value)
			package_path = Path(f"tmp/{rmskin_name}.rmskin")
			await self.rmskin_package.save(package_path)
			rmskin_creation = push_rmskin("theme", self.theme_title.value, self.author.value, rmskin_name)
			image_extension = Path(self.image_preview.filename).suffix
			image_name = img_rename(self.theme_title.value, self.author.value)
			image_path = Path(f"tmp/{image_name}{image_extension}")
			await self.image_preview.save(image_path)
			webp_path = to_webp(image_path)
			image_creation = push_image("theme", self.theme_title.value, self.author.value, image_name)
			updated_json, download_link, image_link, theme_id = update_json("theme", self.theme_title.value, self.author.value, self.description.value, rmskin_name, image_name)
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url=download_link)
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptop-four.github.io/community-themes#{theme_id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
			if self.description.value:
				embed = discord.Embed(title=f"{self.theme_title.value} - {self.author.value}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
			else:
				embed = discord.Embed(title=f"{self.theme_title.value} - {self.author.value}", description="", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="New Community Theme Release", url=self.configs["website"]+"/community-themes")
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)
			image_file = await self.image_preview.to_file(filename="image.png")
			embed.set_image(url="attachment://image.png")
			threads = []
			for thread in self.channel.threads:
				threads.append(thread.name)
			if f"{self.theme_title.value} - {self.author.value}" in threads:
				for thread in self.channel.threads:
					if f"{self.theme_title.value} - {self.author.value}" in thread.name:
						same_thread = thread
				await same_thread.send(embed=embed, file=image_file, view=view)
			else:
				await self.channel.create_thread(name=f"{self.theme_title.value} - {self.author.value}", embed=embed, file=image_file, view=view)
			webp_path.unlink()
			await interaction.followup.send(f"You successfully published **{self.theme_title.value}** in <#{self.channel.id}>", ephemeral=True)

		else:
			await interaction.response.send_message(f"Your theme is being released... Please wait...", ephemeral=True)
			rmskin_name = rmskin_rename("theme", self.theme_title.value, self.author.value)
			package_path = Path(f"tmp/{rmskin_name}.rmskin")
			await self.rmskin_package.save(package_path)
			rmskin_creation = push_rmskin("theme", self.theme_title.value, self.author.value, rmskin_name)
			image_name = img_rename(self.theme_title.value, self.author.value)
			webp_path = Path(f"tmp/{image_name}.webp")
			await self.image_preview.save(webp_path)
			image_creation = push_image("theme", self.theme_title.value, self.author.value, image_name)
			updated_json, download_link, image_link, theme_id = update_json("theme", self.theme_title.value, self.author.value, self.description.value, rmskin_name, image_name)
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			download_button = discord.ui.Button(style=style, label="Download", url=download_link)
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptop-four.github.io/community-themes#{theme_id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
			if self.description.value:
				embed = discord.Embed(title=f"{self.theme_title.value} - {self.author.value}", description=f"{self.description.value}", color=discord.Color.from_rgb(75, 215, 100))
			else:
				embed = discord.Embed(title=f"{self.theme_title.value} - {self.author.value}", description="", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="New Community Theme Release", url=self.configs["website"]+"/community-themes")
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)
			image_file = await self.image_preview.to_file(filename="image.png")
			embed.set_image(url="attachment://image.png")
			threads = []
			for thread in self.channel.threads:
				threads.append(thread.name)
			if f"{self.theme_title.value} - {self.author.value}" in threads:
				for thread in self.channel.threads:
					if f"{self.theme_title.value} - {self.author.value}" in thread.name:
						same_thread = thread
				await same_thread.send(embed=embed, file=image_file, view=view)
			else:
				await self.channel.create_thread(name=f"{self.theme_title.value} - {self.author.value}", embed=embed, file=image_file, view=view)
			webp_path.unlink()
			await interaction.followup.send(f"You successfully published **{self.theme_title.value}** in <#{self.channel.id}>", ephemeral=True)
		package_path.unlink()

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.followup.send(f"Oops! Something went wrong.\n{error}", ephemeral=True)
		traceback.print_tb(error.__traceback__)



class DroptopCommands(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	
	group = app_commands.Group(name="info", description="info command")

	async def variant_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		variants = ["Basic", "Supporter"]
		return [
        	app_commands.Choice(name=variant, value=variant)
	        for variant in variants if current.lower() in variant.lower()
    	]
	
	@group.command(name="droptop")
	@app_commands.describe(
		variant="The Droptop Four variant you want info about"
	)
	@app_commands.autocomplete(variant=variant_autocomplete)
	async def droptop_sub(self, interaction: discord.Interaction, variant: Optional[str] = None) -> None:
		""" Displays info about Droptop Four """
		data = github_reader("data/droptop_info.json")
		version = github_reader("data/version.json")

		if variant:
			if variant == "Basic":
				embed = discord.Embed(title="Droptop Four - Basic Variant", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
				embed.set_thumbnail(url=self.bot.droptopfour_logo)
				for field in data["messages"][0]["content"][1]["fields"]:
					embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
				embed.set_footer(text=data["messages"][0]["content"][1]["footer"])
				await interaction.response.send_message(embed=embed, ephemeral=True)
			
			elif variant == "Supporter":
				embed = discord.Embed(title="Droptop Four - Supporter Variant", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
				embed.set_thumbnail(url=self.bot.droptopfour_logo)
				for field in data["messages"][0]["content"][2]["fields"]:
					embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
				embed.set_footer(text=data["messages"][0]["content"][2]["footer"])
				await interaction.response.send_message(embed=embed, ephemeral=True)
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
			await interaction.response.send_message(embed=embed, ephemeral=True)
			


	async def community_app_name_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		community_apps_names = []
		data = github_reader("data/community_apps/community_apps.json")
		for app in data["apps"]:
			community_apps_names.append(app["app"]["name"])
		return [
        	app_commands.Choice(name=community_app_name, value=community_app_name)
	        for community_app_name in community_apps_names if current.lower() in community_app_name.lower()
    	][:25]

	
	@group.command(name="community_apps")
	@app_commands.describe(
		name="The name of the custom app you want info about (Only 25 elements are shown in the auto-completition list)"
	)
	@app_commands.autocomplete(name=community_app_name_autocomplete)
	async def community_apps_sub(self, interaction: discord.Interaction, name: str) -> None:
		""" Displays info about Droptop Four Community Apps  """

		data = github_reader("data/community_apps/community_apps.json")

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
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptop-four.github.io/community-apps#{id}")
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
		

	async def community_themes_name_autocomplete(self, interaction: discord.Interaction, current: str, ) -> List[app_commands.Choice[str]]:
		community_themes_names = []
		data = github_reader("data/community_themes/community_themes.json")
		for theme in data["themes"]:
			community_themes_names.append(theme["theme"]["name"])
		return [
        	app_commands.Choice(name=community_theme_name, value=community_theme_name)
	        for community_theme_name in community_themes_names if current.lower() in community_theme_name.lower()
    	][:25]

	
	@group.command(name="community_themes")
	@app_commands.describe(
		name="The name of the custom theme you want info about (Only 25 elements are shown in the auto-completition list)"
	)
	@app_commands.autocomplete(name=community_themes_name_autocomplete)
	async def community_themes_sub(self, interaction: discord.Interaction, name: str) -> None:
		"""Displays info about Droptop Four Community Themes"""

		data = github_reader("data/community_themes/community_themes.json")

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
			site_button = discord.ui.Button(style=style, label="See on Website", url=f"https://droptop-four.github.io/community-themes#{id}")
			view.add_item(item=download_button)
			view.add_item(item=site_button)
	
			embed = discord.Embed(title=f"{name} - {author}", description=f"{description}", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="Community Theme Info", url=self.bot.configs["website"]+"/community-themes")
			embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)
			embed.set_image(url=image_url)
			await interaction.response.send_message(embed=embed, view=view)
			
		else:
			await interaction.response.send_message(f"The {name} community theme doesn't exists.", ephemeral=True)
	
	
	@app_commands.command(name="download")
	@app_commands.describe(
		variant="The Droptop Four variant you want download info about"
	)
	@app_commands.autocomplete(variant=variant_autocomplete)
	async def download(self, interaction: discord.Interaction, variant: Optional[str] = None):
		"""Displays downloads info about Droptop Four"""

		data = github_reader("data/droptop_info.json")

		if variant:
			if variant == "Basic":
				view = discord.ui.View()
				style = discord.ButtonStyle.url
				button_b = discord.ui.Button(style=style, label="Download Basic", url="https://github.com/Droptop-Four/Basic-Version/releases/tag/Current-Stable")
				view.add_item(item=button_b)
				embed = discord.Embed(title="Droptop Four", color=discord.Color.from_rgb(75, 215, 100))
				embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
				embed.set_thumbnail(url=self.bot.droptopfour_logo)
				for field in data["messages"][1]["content"][1]["fields"]:
					embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
				embed.set_footer(text=data["messages"][1]["content"][1]["footer"])
				await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
			
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
				await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
			else:
				await interaction.response.send_message(f"The {variant} variant doesn't exists.", ephemeral=True)
		else:
			view = discord.ui.View()
			style = discord.ButtonStyle.url
			button_b = discord.ui.Button(style=style, label="Download Basic", url="https://github.com/Droptop-Four/Basic-Version/releases/tag/Current-Stable")
			button_s = discord.ui.Button(style=style, label="Download Supporter", url="https://gumroad.com/l/droptop")
			view.add_item(item=button_b)
			view.add_item(item=button_s)
			embed = discord.Embed(title="Droptop Four", color=discord.Color.from_rgb(75, 215, 100))
			embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
			embed.set_thumbnail(url=self.bot.droptopfour_logo)
			for field in data["messages"][1]["content"][0]["fields"]:
				embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
			embed.set_footer(text=data["messages"][1]["content"][0]["footer"])
			await interaction.response.send_message(embed=embed, ephemeral=True, view=view)


	@app_commands.command(name="update")
	async def update(self, interaction: discord.Interaction):
		"""Displays update info about Droptop Four"""

		data = github_reader("data/droptop_info.json")

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		button = discord.ui.Button(style=style, label="Download Update", url="https://github.com/Droptop-Four/Update/releases/latest")
		view.add_item(item=button)

		embed = discord.Embed(title="Droptop Four Update", color=discord.Color.from_rgb(75, 215, 100))
		embed.set_author(name="Created by Cariboudjan", url=self.bot.configs["website"], icon_url=self.bot.cari_logo)
		embed.set_thumbnail(url=self.bot.droptopfour_logo)
		for field in data["messages"][2]["content"][0]["fields"]:
			embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
		embed.set_footer(text=data["messages"][2]["content"][0]["footer"])
		await interaction.response.send_message(embed=embed, ephemeral=True, view=view)


	@app_commands.command(name="faq")
	async def faq(self, interaction: discord.Interaction):
		"""Displays the F.A.Q. link"""

		data = github_reader("data/droptop_info.json")

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		button = discord.ui.Button(style=style, label="FAQs", url="https://droptop-four.github.io/faq")
		view.add_item(item=button)

		embed = discord.Embed(title="Droptop Four F.A.Q.", color=discord.Color.from_rgb(75, 215, 100))
		for field in data["messages"][3]["content"][0]["fields"]:
			embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
		await interaction.response.send_message(embed=embed, ephemeral=True, view=view)

	
	@app_commands.command(name="website")
	async def website(self, interaction: discord.Interaction):
		"""Displays the website link"""

		data = github_reader("data/droptop_info.json")

		view = discord.ui.View()
		style = discord.ButtonStyle.url
		button = discord.ui.Button(style=style, label="Website", url="https://droptop-four.github.io")
		view.add_item(item=button)

		embed = discord.Embed(title="Droptop Four website", color=discord.Color.from_rgb(75, 215, 100))
		for field in data["messages"][4]["content"][0]["fields"]:
			embed.add_field(name=field["name"], value=field["content"], inline=field["inline"])
		await interaction.response.send_message(embed=embed, ephemeral=True, view=view)

	

	@app_commands.command(name="new_app_release")
	@app_commands.describe(
		rmskin_package="The package of your Community App",
		image_preview="The image of your Community App",
	)
	async def new_app_release(self, interaction: discord.Interaction, rmskin_package: discord.Attachment, image_preview: discord.Attachment):
		"""Creates a new Community App Release to Github, the website and the discord server."""
		
		channel = self.bot.get_channel(self.bot.configs["appreleases_channel"])

		if rmskin_package.filename.lower().endswith(".rmskin"):
			if image_preview.filename.lower().endswith((".jpg", ".jpeg", ".png")):
				await interaction.response.send_modal(NewAppRelease(self.bot.configs, "jpg", rmskin_package, image_preview, channel))
				
			elif image_preview.filename.lower().endswith(".webp"):
				await interaction.response.send_modal(NewAppRelease(self.bot.configs, "webp", rmskin_package, image_preview, channel))

			else:
				await interaction.response.send_message("No image was found, be sure to put it in the right hitbox the next time.", ephemeral=True)
			
		else:
			await interaction.response.send_message("No rmskin package was found, be sure to put it in the right hitbox the next time.", ephemeral=True)



	@app_commands.command(name="new_theme_release")
	@app_commands.describe(rmskin_package="The package of your Community App",
		image_preview="The image of your Community App",
	)
	async def new_theme_release(self, interaction: discord.Interaction, rmskin_package: discord.Attachment, image_preview: discord.Attachment):
		"""Creates a new Community Theme Release to Github, the website and the discord server."""
		
		channel = self.bot.get_channel(self.bot.configs["themereleases_channel"])

		if rmskin_package.filename.lower().endswith(".rmskin"):
			if image_preview.filename.lower().endswith((".jpg", ".jpeg", ".png")):
				await interaction.response.send_modal(NewThemeRelease(self.bot.configs, "jpg", rmskin_package, image_preview, channel))
				
			elif image_preview.filename.lower().endswith(".webp"):
				await interaction.response.send_modal(NewThemeRelease(self.bot.configs, "webp", rmskin_package, image_preview, channel))

			else:
				await interaction.response.send_message("No image was found, be sure to put it in the right hitbox the next time.", ephemeral=True)
			
		else:
			await interaction.response.send_message("No rmskin package was found, be sure to put it in the right hitbox the next time.", ephemeral=True)



async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DroptopCommands(bot))
