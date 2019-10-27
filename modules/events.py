import discord
from discord.ext import commands
from support import services
from database import dbfunctions
from codeforge import cfevents
from support import log
logger = log.Logger


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Ready notifications
    @commands.Cog.listener()
    async def on_ready(self):
        logger.log(logger.INFO, f"Logged in as: {self.client.user.name}")
        logger.log(logger.INFO, f"Bot ID: {self.client.user.id}")
        logger.log(logger.INFO, "====================================")
        logger.log(logger.OK, "====================================")
        logger.log(logger.VERBOSE, "====================================")
        logger.log(logger.DEBUG, "====================================")
        logger.log(logger.ERROR, "====================================")
        for guild in self.client.guilds:
            logger.log(logger.INFO, f"Connected to {guild}")
            # Add guild to db, add all users of said guild to db afterwards (relational)
            dbfunctions.guild_add(guild)
            dbfunctions.guild_add_users(guild)
        logger.log(logger.INFO, "====================================")
        await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('大家好！'))

    # Guild interactions
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logger.log(logger.INFO, "====================================")
        logger.log(logger.INFO, f"Connected to {guild}")
        logger.log(logger.INFO, "====================================")
        # Add guild to db, add all users of said guild to db afterwards (relational)
        dbfunctions.guild_add(guild)
        dbfunctions.guild_add_users(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logger.log(logger.INFO, "====================================")
        logger.log(logger.INFO, f"Disconnected from {guild}")
        logger.log(logger.INFO, "====================================")
        dbfunctions.guild_remove(guild)

    # Member interaction
    @commands.Cog.listener()
    async def on_member_join(self, member):
        logger.log(logger.VERBOSE, f"{member} joined {member.guild}", member.guild)
        if not member.bot:
            dbfunctions.add_user(member.guild, member)
        if cfevents.check_cf_guild(message.guild.id) :
            await cfevents.cf_on_member_join(member)
        elif not member.bot && not cfevents.check_cf_guild(message.guild.id):
            await services.set_user_auto_roles(member, member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logger.log(logger.VERBOSE, f"{member} left {member.guild}", member.guild)


def setup(client):
    client.add_cog(Events(client))
