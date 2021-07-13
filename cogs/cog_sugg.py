import discord
from discord.ext import commands
import json
import time
import os
import pymongo
from pymongo import MongoClient



cluster = MongoClient(os.getenv("client_id"))
db = cluster["Discord_Droptop"]
collection_s = db["Suggestions"]





class SuggestionCommands(commands.Cog, name="Suggestions"):



    def __init__(self, bot):
        self.bot = bot
	


	


    @commands.command(name='suggest', aliases=['sugg','sug'])
    async def suggest(self, ctx, *, sugg):
        """suggestion command"""
        
        channel = self.bot.get_channel(self.bot.suggchannel)

        
        if ctx.message.attachments:
        	
        	attachment_url = ctx.message.attachments
        	
        	embed1 = discord.Embed(title='New Suggestion By {}'.format(ctx.author.display_name), color=discord.Color.from_rgb(217, 144, 40))
        	
        	embed2 = discord.Embed(color=discord.Color.from_rgb(217, 144, 40))
        	embed2.add_field(name='Suggestion: ', value=sugg)
        	embed2.set_footer(text='UserID: ( {} ) | sID: ( {} )'.format(ctx.author.id, ctx.author.display_name), icon_url=ctx.author.avatar_url)
        	
        	sugg1 = await channel.send(embed=embed1)
        	
        	for url in attachment_url:
        	    await channel.send(url)
        	    
        	sugg2 = await channel.send(embed=embed2)
        	
        	attcs = ' '.join(map(str, attachment_url))
        	
        	post={"UserID":ctx.author.id,"sID":ctx.author.display_name,"Suggestion":sugg,"Attachment":attcs}
            
        	collection_s.insert_one(post)
        	
        	await sugg2.add_reaction("👍")
        	await sugg2.add_reaction("👎")
        	
        	embed = discord.Embed(description='☑️ Your Suggestion Has Been Sent To <#{}> !'.format(channel.id))
        	
        	await ctx.message.delete()
        	embsend = await ctx.send(embed = embed)
        	time.sleep(5)
        	await embsend.delete()
        	
        else:
        	
        	embed = discord.Embed(title=' prova New Suggestion By {}'.format(ctx.author.display_name), color=discord.Color.from_rgb(217, 144, 40))
        	embed.add_field(name='Suggestion: ', value=sugg)
        	embed.set_footer(text='UserID: ( {} ) | sID: ( {} )'.format(ctx.author.id, ctx.author.display_name), icon_url=ctx.author.avatar_url)
        	
        	post={"UserID":ctx.author.id,"sID":ctx.author.display_name,"Suggestion":sugg}
        	
        	suggg = await channel.send(embed=embed)

        	collection_s.insert_one(post)
        	await suggg.add_reaction("👍")
        	await suggg.add_reaction("👎")
        	embed = discord.Embed(description='☑️ Your Suggestion Has Been Sent To <#{}> !'.format(channel.id))
        	await ctx.message.delete()
        	embsend = await ctx.send(embed = embed)
        	time.sleep(5)
        	await embsend.delete()
        	
        	
        	

    @suggest.error
    async def _sug_error(self, ctx, error):
        if isinstance (error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='Syntax Error', color=0xFF2E00)
            embed.add_field(name='{}suggest command'.format(self.bot.command_prefix), value='{}suggestion <message>'.format(self.bot.command_prefix), inline=False)
            embsend=await ctx.send(embed=embed)
            time.sleep(5)
            await ctx.message.delete()
            time.sleep(15)
            await embsend.delete()



	



def setup(bot):
	bot.add_cog(SuggestionCommands(bot))

