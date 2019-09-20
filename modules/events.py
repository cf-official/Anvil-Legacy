import discord
from discord.ext import commands
from support.bcolors import Bcolors
from database import dbfunctions


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Ready notifications
    @commands.Cog.listener()
    async def on_ready(self):
        print(Bcolors.SUCCES + 'Logged in as: ' + self.client.user.name)
        print(Bcolors.SUCCES + 'Bot ID: ' + str(self.client.user.id))
        print(Bcolors.NOTIFICATION + '------')
        for guild in self.client.guilds:
            print(f"Connected to server: {guild}")
            dbfunctions.guild_add(guild)
        print('------')
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('大家好！'))

    # Guild interactions
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(Bcolors.NOTIFICATION + '------')
        print(f"Connected to server: {guild}")
        print('------')
        dbfunctions.guild_add(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(Bcolors.NOTIFICATION + '------')
        print(f"Disconnected from server: {guild}")
        print('------')
        dbfunctions.guild_remove(guild)

    # Error listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You are missing a required argument.')
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send('You are using a faulty argument.')
        else:
            print(Bcolors.FAIL + f'[Error] {ctx.message.content} -> {error}')

    # Member interaction
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(Bcolors.OKBLUE + f'{member} has joined {member.guild}.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(Bcolors.OKBLUE + f'{member} has left {member.guild}.')

    # Message interaction
    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author
        if user.bot is False:
            dbfunctions.update_user_messages(user, 1)
            print(dbfunctions.check_user_last_message(user))
            if dbfunctions.check_user_last_message(user):
                dbfunctions.update_user_activity(user, 1)

def setup(client):
    client.add_cog(Events(client))
