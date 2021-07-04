import os
import discord
from discord.ext import commands
import time
import pymongo
from pymongo import MongoClient



cluster = MongoClient(os.getenv("client_id"))
db = cluster["Discord_Droptop"]
collection_bw = db["BannedWords"]



class ModCommands(commands.Cog, name='Moderation'):
	'''These are the Mod Commands'''
	


	def __init__(self, bot):
		self.bot = bot	



	@commands.Cog.listener()
	async def on_message(self,message):
		if message.author.id == self.bot.user.id:
			return
		elif message.author.id == self.bot.author_id:
			return
		elif message.author.id == self.bot.cari_id:
			return
		else: 
			with open('bannedwords.txt') as file:
				file = file.read().split()
			for bannedword in file:
				if bannedword in message.content.lower():
					await message.delete()



	@commands.command(name='bannedwords', aliases=['bw','banwords','banword','bannedword'])
	@commands.has_any_role(800217789343727657, 801741190227165236)
	async def bannedwords(self, ctx, arg1=None, arg2=None):
		bwls=['ls','list','all',]
		bwadd=['add',]
		bwremove=['rm','remove','delete',]
		if arg1 is None:
			mydoc = collection_bw.find()
			f = open("bannedwords.txt", "w")
			for x in mydoc:
				query=x['name']+' '
				f.write(query)
			f.close()
			f = open("bannedwords.txt", "r")
			result=f.read()
			if result:
				await ctx.send('The banned words are: '+result)
			else:
				await ctx.send('Currently there are no banned words.')
		if arg1 in bwls:
			mydoc = collection_bw.find()
			f = open("bannedwords.txt", "w")
			for x in mydoc:
				query=x['name']+' '
				f.write(query)
			f.close()
			f = open("bannedwords.txt", "r")
			if result:
				await ctx.send('The banned words are: '+result)
			else:
				await ctx.send('Currently there are no banned words.')
		elif arg1 in bwadd:
			if arg2 is None:
				await ctx.send('You need to add a word to be added to the banned words list.')
			else:
				arg2=arg2.lower()
				post={"UserID":ctx.author.id,"sID":ctx.author.display_name,"name":arg2}
				collection_bw.insert_one(post)
				await ctx.send('`{0}` was added to the banned words list.'.format(arg2))
				mydoc = collection_bw.find()
				f = open("bannedwords.txt", "w")
				for x in mydoc:
					query=x['name']+' '
					f.write(query)
				f.close()
		elif arg1 in bwremove:
			if arg2 is None:
				await ctx.send('You need to add a word to be removed from the banned words list.')
			else:
				arg2=arg2.lower()
				query={"name":arg2}
				collection_bw.delete_one(query)
				await ctx.send('`{0}` was removed from the banned words list.'.format(arg2))
				mydoc = collection_bw.find()
				f = open("bannedwords.txt", "w")
				for x in mydoc:
					query=x['name']+' '
					f.write(query)
				f.close()
		else:
			pass


	@commands.command(name='kick', aliases=[])
	@commands.has_any_role(800217789343727657, 801741190227165236)
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		await ctx.guild.kick(user=member, reason=reason)
		channel = self.bot.get_channel(856485433496174592)
		embed = discord.Embed(title=f"{ctx.author.name} kicked: {member.name}", description=reason)
		await channel.send(embed=embed)

	@commands.command(name='ban', aliases=[])
	@commands.has_any_role(800217789343727657, 801741190227165236)
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		await ctx.guild.ban(user=member, reason=reason)
		channel = self.bot.get_channel(856485433496174592)
		embed = discord.Embed(title=f"{ctx.author.name} banned: {member.name}", description=reason)
		await channel.send(embed=embed)


	@commands.command(name='unban', aliases=[])
	@commands.has_any_role(800217789343727657, 801741190227165236)
	async def unban(self, ctx, member, *, reason=None):
		member = await self.bot.fetch_user(int(member))
		await ctx.guild.unban(member, reason=reason)
		channel = self.bot.get_channel(856485433496174592)
		embed = discord.Embed(title=f"{ctx.author.name} unbanned: {member.name}", description=reason)
		await channel.send(embed=embed)
	

	@commands.command(name='purge', aliases=[])
	@commands.has_any_role(800217789343727657, 801741190227165236)
	async def purge(self, ctx, amount=15):
		await ctx.channel.purge(limit=amount+1)
		channel = self.bot.get_channel(856485433496174592)
		embed = discord.Embed(title=f"{ctx.author.name} purged: {ctx.channel.name}", description=f"{amount} messages were cleared")
		await channel.send(embed=embed)


def setup(bot):
	bot.add_cog(ModCommands(bot))
