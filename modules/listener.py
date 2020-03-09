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
        # Make sure bot doesn't reply to DM usage
        if ctx.guild is None: return False

        # Make sure owners always get a free pass
        if ctx.author.guild_permissions.administrator: return True

        # Also make sure command is being used in allowed channel
        channels = services.get_channels_by_id(ctx.guild, dbfunctions.retrieve_channels(ctx.guild.id))
        if channels:
            if ctx.channel not in channels: return False

        # If it somehow passes all conditions but fails to return properly.
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

        # Make sure message wasn't sent through DM
        if not hasattr(user, 'guild'): return

        # Make sure user is not a bot and user is not None
        if user.bot is False and user is not None:
            await services.set_user_auto_roles(user, user.guild)

            # Increment message count
            dbfunctions.update_user_messages(user.guild, user, 1)

            # Check if last message sent was longer than a minute ago
            if dbfunctions.check_user_last_message(user, user.guild.id):
                # Add to activity score
                dbfunctions.update_user_activity(user.guild, user, 1)

            # Check if the message was sent in CodeForge
            if cfevents.check_cf_guild(message.guild.id):
                # Passthrough to the CodeForge specefic message handler???
                await cfevents.cf_on_message_create(message)

            # Calculate odds to award coins
            if services.attempt_chance(100, 5)[0]:
                # Decide how many coins, and apply coin reward
                result, roll = services.attempt_chance(30, 30, 10)
                dbfunctions.update_user_tokens(user.guild, user, roll)

                # Attempt to add reactions to showcase token gain
                try:
                    await message.add_reaction("💲")
                    await services.numerical_reaction(message, roll)
                except Exception as e:
                    # Tried to apply reactions to a no longer existing message, most likely.
                    logger.log(logger.VERBOSE, e, user.guild)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        if guild is None: return
        user = guild.get_member(payload.user_id)
        # Filter out bots
        if user.bot: return

        channel = guild.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            # Couldn't fetch the message, probably because it was removed by another bot (looking at you sigma)
            # logger.log(logger.ERROR, f"(events.py) on_raw_reaction_add (1): {e}", guild)
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
                logger.log(logger.ERROR, f"(events.py) on_raw_reaction_add (2): {e}", guild)

            if dbfunctions.check_reaction(str(emoji_id), guild_id):
                # Give karma to user if karma event returns true (karma gain available from this person!)
                if dbfunctions.set_karma_event(channel, user, message.author, guild_id):
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
