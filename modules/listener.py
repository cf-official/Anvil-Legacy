from discord.ext import commands
from support import config as cfg
from support import services
from database import dbfunctions
from codeforge import cfevents
from support import log
logger = log.Logger


class Listener(commands.Cog):
    def __init__(self, client):
        self.client = client

    def cog_unload(self):
        print('cleanup goes here')

    def bot_check(self, ctx):
        # Filter out DM's
        if ctx.guild is None: return False

        # Guild admins get a pass
        if ctx.author.guild_permissions.administrator: return True

        # If custom bot-channels are set, disallow usage outside them
        allowed_channels = services.get_channels_by_id(ctx.guild, dbfunctions.retrieve_channels(ctx.guild.id))
        if allowed_channels:
            if ctx.channel not in allowed_channels: return False

        return True

    def bot_check_once(self, ctx):
        # Not being used for now
        return True

    async def cog_check(self, ctx):
        print('cog local check')
        return await ctx.bot.is_owner(ctx.author)

    async def cog_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    async def cog_before_invoke(self, ctx):
        print('cog local before: {0.command.qualified_name}'.format(ctx))

    async def cog_after_invoke(self, ctx):
        print('cog local after: {0.command.qualified_name}'.format(ctx))

    # Message interaction
    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author

        # Filter out DM's, Bots and invalid users
        if not hasattr(user, 'guild') or user.bot is True or user is None: return

        # Update user roles and stats
        await services.set_user_auto_roles(user, user.guild)
        dbfunctions.update_user_messages(user.guild, user, 1)
        if dbfunctions.check_user_last_message(user, user.guild.id):
            dbfunctions.update_user_activity(user.guild, user, 1)

        # Handle CF specific messages
        if cfevents.check_cf_guild(message.guild.id):
            await cfevents.cf_on_message_create(message)

        # Randomly award tokens
        if services.attempt_chance(1, 100, 5)[0]:
            result, roll = services.attempt_chance(1, 10, 10)
            dbfunctions.update_user_tokens(user.guild, user, roll)

            # Give visual feedback of tokens won
            await services.numerical_reaction(message, roll)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Guilds only
        guild = self.client.get_guild(payload.guild_id)
        if guild is None: return
        # Non-bot users only
        user = guild.get_member(payload.user_id)
        if user.bot: return

        # Message fetch and author check
        channel = guild.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            # Message most likely not available
            return
        if message.author is user or message.author.bot: return

        # Format reaction to proper emoji
        guild_id = guild.id
        emoji_id = payload.emoji
        try:
            if emoji_id.id:
                emoji_id = emoji_id.id
        except AttributeError:
            pass

        # Check emoji for guild karma reaction
        if not dbfunctions.check_reaction(str(emoji_id), guild_id): return

        # Check if user is eligible for karma
        if not dbfunctions.set_karma_event(channel, user, message.author, guild_id): return

        # Award karma
        logger.log(logger.VERBOSE, f"{user} gave {message.author} karma.", guild)
        dbfunctions.update_user_karma(guild, message.author, 1)

    # Error listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.guild is None:
            return
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


def setup(client):
    client.add_cog(Listener(client))
