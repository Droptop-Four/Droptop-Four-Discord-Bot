'''
Cog Name: Developer Commands
Commands: 4
Slash Commands: 0
'''


import discord
from discord.ext import commands
import time


class DeveloperCommands(commands.Cog, name='Developer'):
    '''These are the Developer commands'''


    def __init__(self, bot):
        self.bot = bot


    async def cog_check(self, ctx):
        '''The default check for this cog whenever a command is used. Returns True if the command is allowed.'''
        return ctx.author.id == self.bot.author_id


    @commands.command(name='reload',aliases=['rl'], help='This command reloads a cog')
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def reload(self, ctx, cog):
        '''Reloads a cog'''
        
        extensions = self.bot.extensions  # A list of the bot's cogs/extensions.
        if cog == 'all':  # Lets you reload all cogs at once
            for extension in extensions:
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            await ctx.send('Done')
        if cog in extensions:
            self.bot.unload_extension(cog)  # Unloads the cog
            self.bot.load_extension(cog)  # Loads the cog
            await ctx.send('Done')  # Sends a message where content='Done'
        else:
            await ctx.send('Unknown Cog')  # If the cog isn't found/loaded.


    @commands.command(name="unload", aliases=['ul'], help='This command unloads a cog')
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def unload(self, ctx, cog):
        '''Unloads a cog'''
        
        extensions = self.bot.extensions
        if cog not in extensions:
            await ctx.send("Cog is not loaded!")
            return
        self.bot.unload_extension(cog)
        await ctx.send(f"`{cog}` has successfully been unloaded.")


    @commands.command(name="load", aliases=['l'], help='This command loads a cog')
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def load(self, ctx, cog):
        '''Loads a cog'''
        
        try:
            self.bot.load_extension(cog)
            await ctx.send(f"`{cog}` has successfully been loaded.")

        except commands.errors.ExtensionNotFound:
            await ctx.send(f"`{cog}` does not exist!")


    @commands.command(name="listcogs", aliases=['lc'], help='This command returns a list of all enabled cogs')
    # Admin Role ID, Mod Role ID
    @commands.has_any_role(800217789343727657, 801741190227165236)
    async def listcogs(self, ctx):
        '''Returns a list of all enabled cogs'''
        
        base_string = "```css\n"  # Gives some styling to the list (on pc side)
        base_string += "\n".join([str(cog) for cog in self.bot.extensions])
        base_string += "\n```"
        await ctx.send(base_string)


def setup(bot):
    bot.add_cog(DeveloperCommands(bot))
