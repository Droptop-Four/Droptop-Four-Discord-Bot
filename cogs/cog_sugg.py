import discord
from discord import app_commands
from discord.ext import commands

import os
import pymongo
from pymongo import MongoClient


cluster = MongoClient(os.getenv("mongodb_id"))
db = cluster[os.getenv("db_cluster")]
collection_s = db["Suggestions"]


class SuggestionCommands(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
    
	
	@app_commands.command(name="suggest")
	@app_commands.describe(
		suggestion="Your suggestion about Droptop",
		image="Optional image you want to attach"
	)
	async def suggest(self, interaction: discord.Interaction, suggestion: str, image: discord.Attachment = None):
		""" Lets you make a suggestion """
		
		channel = self.bot.get_channel(self.bot.configs["suggestions_channel"])

		await interaction.response.send_message(f"Your suggestion is being sent to <#{channel.id}>...", ephemeral=True)

		embed = discord.Embed(title=f"New Suggestion By {interaction.user.display_name}", color=discord.Color.from_rgb(217, 144, 40))
		embed.add_field(name="Suggestion: ", value=suggestion)
		embed.set_footer(text=f"UserID: ( {interaction.user.id} ) | sID: ( {interaction.user.display_name} )", icon_url=interaction.user.avatar.url)

		if image:
			image_file = await image.to_file(filename="image.png")
			embed.set_image(url="attachment://image.png")
			post = {"UserID": interaction.user.id, "sID": interaction.user.display_name, "Suggestion": suggestion}
			suggg = await channel.send(file=image_file, embed=embed)
			

		else:
			post = {"UserID": interaction.user.id, "sID": interaction.user.display_name, "Suggestion": suggestion}
			suggg = await channel.send(embed=embed)
		collection_s.insert_one(post)
		await suggg.add_reaction("👍")
		await suggg.add_reaction("👎")
		await suggg.create_thread(name="Discussion")
		embed = discord.Embed(description=f"☑️ Your Suggestion Has Been Sent To <#{channel.id}> !")
		await interaction.followup.send(embed=embed, ephemeral=True)



async def setup(bot: commands.Bot):
	await bot.add_cog(SuggestionCommands(bot))
