import discord
from discord.ext import commands
from support.bcolors import Bcolors


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
        print('------')
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('大家好！'))

    # Error listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You are missing a required argument.')
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send('You are using a faulty argument.')
        else:
            print(Bcolors.FAIL + f'[Error] {ctx.message.content} -> {error}')

    # Members Joining/Leaving servers
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'{member} has joined {member.guild}.')

def setup(client):
    client.add_cog(Events(client))
