import discord
from discord.ext import tasks, commands
from support.bcolors import Bcolors
from support import services
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
            # Add guild to db, add all users of said guild to db afterwards (relational)
            dbfunctions.guild_add(guild)
            dbfunctions.guild_add_users(guild)
        print('------')
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('大家好！'))

    # Guild interactions
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(Bcolors.NOTIFICATION + '------')
        print(f"Connected to server: {guild}")
        print('------')
        # Add guild to db, add all users of said guild to db afterwards (relational)
        dbfunctions.guild_add(guild)
        dbfunctions.guild_add_users(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(Bcolors.NOTIFICATION + '------')
        print(f"Disconnected from server: {guild}")
        print('------')
        dbfunctions.guild_remove(guild)
    '''
    # Error listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You are missing a required argument.')
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send('You are using a faulty argument.')
        else:
            print(Bcolors.FAIL + f'[Error] {ctx.message.content} -> {error}')
    '''
    # Member interaction
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(Bcolors.OKBLUE + f'{member} has joined {member.guild}.')
        await services.set_user_auto_roles(member, member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(Bcolors.OKBLUE + f'{member} has left {member.guild}.')

    # Message interaction
    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author
        if user.bot is False:
            await services.set_user_auto_roles(user, user.guild)
            # Increment message count
            dbfunctions.update_user_messages(user.guild, user, 1)
            # Check if last message sent was longer than a minute ago
            if dbfunctions.check_user_last_message(user, user.guild.id):
                # Add to activity score
                dbfunctions.update_user_activity(user.guild, user, 1)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # No giving karma to yourself or to bots
        if reaction.message.author is not user and reaction.message.author.bot is False and user.bot is False:
            guild_id = user.guild.id
            emoji_id = reaction.emoji
            try:
                emoji_id = emoji_id.id
            except AttributeError:
                pass
            except Exception as e:
                print(Bcolors.FAIL + f"[Error] {e} \nIn events.py : on_reaction_add")

            if dbfunctions.check_reaction(str(emoji_id), guild_id):
                # Give karma to user if karma event returns true (karma gain available from this person!)
                if dbfunctions.set_karma_event(user, reaction.message.author, guild_id):
                    print(Bcolors.OKBLUE + f"In {reaction.message.guild}, {user} gave {reaction.message.author} karma")
                    dbfunctions.update_user_karma(user.guild, reaction.message.author, 1)


def setup(client):
    client.add_cog(Events(client))
