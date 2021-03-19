import discord
import json
from discord.ext import commands
from replit import db



class RRCommands(commands.Cog, name='RR commands'):
	'''These are the RR Commands'''
	
	def __init__(self, bot):
		self.bot = bot
	

	@commands.Cog.listener()
	async def on_raw_reaction_add(payload):
		if payload.member.bot:
			pass
		
		else:
			with open('reactrole.json') as react_file:
				data = json.load(react_file)
				for x in data:
					if x['emoji'] == payload.emoji.name:
						role = discord.utils.get(commands.Cog.get_guild(
							payload.guild_id).roles, id=x['role_id'])
						
						await payload.member.add_roles(role)


	@commands.Cog.listener()
	async def on_raw_reaction_remove(payload):
		
		with open('reactrole.json') as react_file:
			data = json.load(react_file)
			for x in data:
				if x['emoji'] == payload.emoji.name:
					role = discord.utils.get(commands.Cog.get_guild(
						payload.guild_id).roles, id=x['role_id'])
					
					await commands.Cog.get_guild(commands.Cog.guild_id).get_member(commands.Cog.user_id).remove_roles(role)
                    

	@commands.command()
# @commands.has_permissions(administrator=True, manage_roles=True)
	async def reactrole(self, emoji, role: discord.Role, *, message):
		
		emb = discord.Embed(description=message)
		msg = await self.bot.channel.send(embed=emb)
		await msg.add_reaction(emoji)
		
		with open('reactrole.json') as json_file:
			data = json.load(json_file)
			
			
			new_react_role = {'role_name': role.name, 
				'role_id': role.id,
        'emoji': emoji,
        'message_id': msg.id}
			
			
			data.append(new_react_role)
		
		
		with open('reactrole.json', 'w') as f:
			json.dump(data, f, indent=4)


	
	
	
	

def setup(bot):
	bot.add_cog(RRCommands(bot))