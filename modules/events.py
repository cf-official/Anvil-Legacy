import discord
from discord.ext import commands
from support.bcolors import Bcolors
from support import services
from database import dbfunctions
from support import config as cfg
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

    # Error listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You are missing a required argument.')
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send('You are using a faulty argument.')
        elif isinstance(error, commands.CommandNotFound):
            return
        # Rest of errors/issues
        else:
            logger.log(logger.ERROR, f"{ctx.message.content} resulted in;\n{error}")
        # Add error emoji
        await ctx.message.add_reaction(cfg.feedback_error_emoji_id)

    # Member interaction
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await services.console_log(member.guild, Bcolors.LIGHT_BLUE, f"{member} joined.")
        if not member.bot:
            dbfunctions.add_user(member.guild, member)
            await services.set_user_auto_roles(member, member.guild)
        await cfevents.cf_on_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await services.console_log(member.guild, Bcolors.LIGHT_BLUE, f"{member} left.")

    # Message interaction
    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author
        if user.bot is False and user is not None:
            await services.set_user_auto_roles(user, user.guild)
            # Increment message count
            dbfunctions.update_user_messages(user.guild, user, 1)
            # Check if last message sent was longer than a minute ago
            if dbfunctions.check_user_last_message(user, user.guild.id):
                # Add to activity score
                dbfunctions.update_user_activity(user.guild, user, 1)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
        # Filter out bots
        if user.bot: return

        channel = guild.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            # Couldn't fetch the message, probably because it was removed by another bot (looking at you sigma)
            await services.console_log(str(guild), Bcolors.RED, f"{e}\nIn events.py : on_reaction_add")
            return

        reaction = payload.emoji

        # No giving karma to yourself or to bots
        if message.author is not user and message.author.bot is False:
            guild_id = guild.id
            emoji_id = reaction
            try:
                if emoji_id.id:
                    emoji_id = emoji_id.id
            except AttributeError:
                pass
            except Exception as e:
                await services.console_log(guild, Bcolors.RED, f"{e}\nIn events.py : on_reaction_add")

            if dbfunctions.check_reaction(str(emoji_id), guild_id):
                # Give karma to user if karma event returns true (karma gain available from this person!)
                if dbfunctions.set_karma_event(channel, user, message.author, guild_id):
                    await services.console_log(guild, Bcolors.YELLOW, f"{user} gave {message.author} karma.")
                    dbfunctions.update_user_karma(guild, message.author, 1)


def setup(client):
    client.add_cog(Events(client))
