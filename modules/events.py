import discord
from discord.ext import commands, tasks
from support import services
from database import dbfunctions
from codeforge import cfevents
from support import log
logger = log.Logger


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.status_list_index = 0
        self.status_list = ["大家好！", "सभी को नमस्कार!", "Hallo allemaal!", "Hello Everyone!", "Hallo zusammen!",
                            "みなさん、こんにちは！", "Bonjour à tous", "¡Hola a todos!"]

    # BG Task for looping status' happens here
    # Add fetching status list from DB later on
    # Add actual looping through list later on
    @tasks.loop(seconds=30)
    async def update_status(self):
        await self.client.change_presence(activity=discord.Game(self.status_list[self.status_list_index]))
        self.status_list_index = self.status_list_index + 1 if self.status_list_index < len(self.status_list) - 1 else 0

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
        self.update_status.start()

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
            await services.set_user_auto_roles(member, member.guild)
        await cfevents.cf_on_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logger.log(logger.VERBOSE, f"{member} left {member.guild}", member.guild)


def setup(client):
    client.add_cog(Events(client))
