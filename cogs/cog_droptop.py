import discord
from discord.ext import commands
import time
from datetime import date, datetime
import json
import os
import re
import pymongo
from pymongo import MongoClient

now = datetime.now()

cluster = MongoClient(os.getenv("client_id"))
db = cluster["Discord_Droptop"]
collection_d = db["BetaPrg"]



class InfoCommands(commands.Cog, name='Info'):
	'''These are the Info Commands'''
	


	def __init__(self, bot):
		self.bot = bot


	@commands.command(name='info', help='This command displays info about Droptop Four', aliases=['Droptop', 'Dt'])
	async def info(self, ctx, arg = None):

		basic=['basic', 'Basic', 'base', 'Base']
		supporter=['supporter', 'Supporter', 'supp', 'Supp', 'sup', 'Sup']

		if arg == None:
			embed1=discord.Embed(title='Droptop Four', color=discord.Color.from_rgb(75, 215, 100))
			embed1.set_author(name="Created by Cariboudjan", url="https://blacksquare88.wixsite.com/droptop4", icon_url='https://cdn.discordapp.com/avatars/584542239900827665/8d070369e6169444ad45c479ef0eec9a.png?size=1024')
			embed1.set_thumbnail(url='https://cdn.discordapp.com/icons/800124057923485728/7e8f7f08dce1d220711ee2488d497c8f.webp?size=1024')
			embed1.add_field(name="What is it?", value="Droptop Four is a popular dropdown app launcher for Windows & Rainmeter.\nIt is available in two version, a `Basic` one, free, and a `Supporter` one, with a \'pay what you want\' donation.\nBoth versions have 14 system tray apps, the Always Show option to make it accessible everywhere on top of your desktop and a lot more.", inline=False)
			embed1.add_field(name="Basic Version", value='The `Basic` version has:\n - 7 home bottons icons\n - 6 fully-customizable toolbars\n - 4 themes to choose from', inline=True)
			embed1.add_field(name='Supporter Version', value='The `Supporter` version has:\n - 300 home buttons icons\n - 12 fully-customizable toolbars\n - 22 themes to choose from', inline=True)
			embed1.set_footer(text="To see further infos on one of the two versions type {0}info basic or {0}info supporter".format(self.bot.command_prefix))

			await ctx.send(embed=embed1)

		if arg in basic:
			embed2=discord.Embed(title='Droptop Four Basic Version', color=discord.Color.from_rgb(75, 215, 100))
			embed2.set_author(name="Created by Cariboudjan", url="https://blacksquare88.wixsite.com/droptop4", icon_url='https://cdn.discordapp.com/avatars/584542239900827665/8d070369e6169444ad45c479ef0eec9a.png?size=1024')
			embed2.set_thumbnail(url='https://cdn.discordapp.com/icons/800124057923485728/7e8f7f08dce1d220711ee2488d497c8f.webp?size=1024')
			embed2.add_field(name="What is it?", value="This is the Basic and free version of droptop.", inline=False)
			embed2.add_field(name="Perks", value='The `Basic` version has:\n - 7 home bottons icons\n - 6 fully-customizable toolbars\n - 4 themes to choose from', inline=False)
			embed2.add_field(name="Download", value='To install it you have to download it on the DeviantArt page of Droptop Four:\nhttps://www.deviantart.com/cariboudjan/art/droptop-four-762812007\nTo see further explanations on download methods type `{}download`'.format(self.bot.command_prefix), inline=False)

			await ctx.send(embed=embed2)
		
		if arg in supporter:
			embed3=discord.Embed(title='Droptop Four Supporter Version', color=discord.Color.from_rgb(75, 215, 100))
			embed3.set_author(name="Created by Cariboudjan", url="https://blacksquare88.wixsite.com/droptop4", icon_url='https://cdn.discordapp.com/avatars/584542239900827665/8d070369e6169444ad45c479ef0eec9a.png?size=1024')
			embed3.set_thumbnail(url='https://cdn.discordapp.com/icons/800124057923485728/7e8f7f08dce1d220711ee2488d497c8f.webp?size=1024')
			embed3.add_field(name="What is it?", value="This is the Supporter version of droptop.\nTo download it you can pay what you want through Gumroad.", inline=False)
			embed3.add_field(name='Perks', value='The `Supporter` version has:\n - 300 home buttons icons\n - 12 fully-customizable toolbars\n - 22 themes to choose from', inline=False)
			embed3.add_field(name="Download", value='To install it you have to:\n1)	download the Basic version on the DeviantArt page of Droptop Four (https://www.deviantart.com/cariboudjan/art/droptop-four-762812007)\n2)	download the Supporter update through Gumroad choosing how much you want to pay for it (from 0$) (https://gumroad.com/l/droptop)\nTo see further explanations on download methods type `{}download`'.format(self.bot.command_prefix), inline=False)

			await ctx.send(embed=embed3)


	@commands.command(name='download', help='This command returns the download possibilities', aliases=['dl', 'down'])
	async def download(self, ctx):
		down=discord.Embed(title='Droptop Four Downloads', color=discord.Color.from_rgb(75, 215, 100))
		down.set_author(name="Created by Cariboudjan", url="https://blacksquare88.wixsite.com/droptop4", icon_url='https://cdn.discordapp.com/avatars/584542239900827665/8d070369e6169444ad45c479ef0eec9a.png?size=1024')
		down.set_thumbnail(url='https://cdn.discordapp.com/icons/800124057923485728/7e8f7f08dce1d220711ee2488d497c8f.webp?size=1024')
		down.add_field(name="Where to download?", value="The Droptop **Base** version can be downloaded on the DeviantArt page of Droptop *[https://www.deviantart.com/cariboudjan/art/droptop-four-762812007]* or by being redirected to it on the Droptop Official Site *[https://blacksquare88.wixsite.com/droptop4]* (for help about the Base version type `{0}info base`)\n\nThe Droptop **Supprter** version can be downloaded after paying what you want on Gumroad *[https://gumroad.com/l/droptop]* (for help about the Supporter version type `{0}info supporter`)".format(self.bot.command_prefix), inline=False)

		await ctx.send(embed=down)


	@commands.command(name='faq', help='This command returns the F.A.Q. link', aliases=['f.a.q'])
	async def faq(self, ctx):
		faq=discord.Embed(title='Droptop Four F.A.Q.', color=discord.Color.from_rgb(75, 215, 100))
		faq.add_field(name="Where do I find the FAQs?", value="You can find the FAQs at https://blacksquare88.wixsite.com/droptop4/faq.", inline=False)

		await ctx.send(embed=faq)

	
	@commands.command(name='beta', help='This command sends informations on how to participate to the beta program', aliases =['beta-tester', 'betatester'])
	
	async def beta(self, ctx, member: discord.Member=None):

		embed=discord.Embed(title='Beta Program', description='Enroll now to the Droptop Four Beta Program! The procedure is quite easy, just follow the guidelines below!', color=0x409bda)
		embed.set_author(name="Droptop Four", url="https://blacksquare88.wixsite.com/droptop4", icon_url=self.bot.user.avatar_url)
		embed.add_field(name='How', value='To enroll you have to have a Gmail account and send me the command `{0}beta-apply \"<name>\" \"<Gmail address>\"`'.format(self.bot.command_prefix), inline=False)
		embed.add_field(name='IMPORTANT!!', value='You have to follow the syntax of the command or your subscription wont be guaranteed.\n**REMEMBER TO USE QUOTATION MARKS**', inline=False)
		embed.add_field(name='Example', value='`{0}beta-apply \"John Doe\" \"john.doe@gmail.com\"`'.format(self.bot.command_prefix), inline=False)

		if member is not None:
			channel=member.dm_channel
			if channel is None:
				channel=await member.create_dm()
			await channel.send(embed=embed)
		else:
			await ctx.author.send(embed=embed)
		
		embed2=discord.Embed(title='CHECK YOUR PMs (Personal Messages)!')
		embsend=await ctx.send(embed=embed2)
		time.sleep(5)
		await embsend.delete()

		
	@commands.command(name='beta-apply', help='This command sends your personal details to participate in the beta program')
	@commands.dm_only()
	async def bapply(self, ctx, name, gmail):

		server = self.bot.get_guild(self.bot.serverid)
		role = discord.utils.get(server.roles, id=self.bot.betarole)
		member = server.get_member(ctx.message.author.id)

		if member:

			if role in member.roles:
				await ctx.send("You already are a beta tester")

			else:
				email = gmail
				if re.search("@gmail.com$", email):

					post={"DateTime":now.strftime("%d/%m/%Y %H:%M:%S"),"UserID":ctx.author.id,"sID":ctx.author.display_name,"Name":name,"Gmail":gmail}


					embed = discord.Embed(title='Beta Program Enrollment', description='Your informations are being sent...', color=0x409bda)
					embed.add_field(name='Your Informations:', value='```\nUserID: {0}\nsID: {1}\nName: {2}\nGmail: {3}\nDateTime: {4} UTC\n```'.format((ctx.author.id), (ctx.author.display_name), (name), (gmail), (now.strftime("%d/%m/%Y %H:%M:%S"))), inline=False)
					await ctx.send(embed=embed)
					
					collection_d.insert_one(post)

					embed2 = discord.Embed(title='Beta Program Enrollment', description='Registration of <@{0}>'.format(ctx.author.id), color=0x409bda)
					embed2.add_field(name='Informations:', value='```\nUserID: {0}\nsID: {1}\nName: {2}\nGmail: {3}\nDateTime: {4} UTC\n```'.format((ctx.author.id), (ctx.author.display_name), (name), (gmail), (now.strftime("%d/%m/%Y %H:%M:%S"))), inline=False)

					channel=self.bot.get_channel(self.bot.betachannel)
					await channel.send(embed=embed2)
					# print('valid email')

					await member.add_roles(role)

				else:
					error=discord.Embed(title='Wrong eMail!', description='**The mail you put is not valid!**\nRemember it must be a **gmail** address, it must ends with `@gmail.com`', color=0xF70600)
					await ctx.send(embed=error)
					# print('invalid email\nERROR')

		else:
			await ctx.send("You are not a member")



	@bapply.error
	async def _bapply_error(self, ctx, error):
		if isinstance (error, commands.PrivateMessageOnly):
			embed = discord.Embed(title='This command can be used only in PMs!', description='Since you have to send personal informations, you have to use this command in a PM (Private Message) with the bot.', color=0xFF2E00)
			embsend=await ctx.send(embed=embed)
			time.sleep(1)
			await ctx.message.delete()
			time.sleep(15)
			await embsend.delete()





def setup(bot):
	bot.add_cog(InfoCommands(bot))