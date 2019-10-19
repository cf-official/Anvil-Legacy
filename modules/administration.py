import discord
from discord.ext import commands
from emoji import UNICODE_EMOJI
from database import dbfunctions
from support import log
logger = log.Logger

from support import services


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Set custom prefix to guild
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, *, new_prefix):
        dbfunctions.set_guild_prefix(ctx.guild, new_prefix)
        logger.log(logger.VERBOSE, f"{ctx.author} changed server prefix to {new_prefix}", ctx.guild)

    # Set karma reaction emoji
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_karma_reaction(self, ctx, emoji):
        # Try for the custom emoji
        emoji_id = ""
        try:
            emoji_id = await commands.EmojiConverter().convert(ctx, emoji)
            emoji_id = emoji_id.id
            # If the bot has access to the emoji, but it's not part of the ctx.guild, remove it
            matching_emoji = sum(1 for x in ctx.guild.emojis if x.id is int(emoji_id))
            if matching_emoji == 0:
                emoji_id = ""
        except commands.errors.BadArgument:
            # Check for non-custom emoji
            if emoji in UNICODE_EMOJI:
                emoji_id = emoji
        except Exception as e:
            logger.log(logger.ERROR, f"(administration.py), set_karma_reaction (1): {e}", ctx.guild)
        if emoji_id == "":
            logger.log(logger.ERROR, f"administration.py, set_karma_reaction (2): tried to use inaccesible emoji.", ctx.guild)
        else:
            dbfunctions.set_guild_karma_emoji(ctx.guild, emoji_id)
            logger.log(logger.VERBOSE, f"{ctx.author} set the karma emoji to {emoji_id}", ctx.guild)

    # Set log_channel_id
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_log_channel_id(self, ctx, channel: discord.TextChannel = None):
        logger.log(logger.VERBOSE, f"{ctx.author} set logging channel to {channel}", ctx.guild)
        if channel is None:
            dbfunctions.set_guild_log_channel(ctx.guild, None)
        else:
            dbfunctions.set_guild_log_channel(ctx.guild, channel.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_role(self, ctx, role: discord.Role, point_req=0, karma_req=0):
        logger.log(logger.VERBOSE, f"{ctx.author} added {role} with point req {point_req} and karma req {karma_req}", ctx.guild)
        dbfunctions.add_role(ctx.guild.id, role, point_req, karma_req)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, role: discord.Role):
        logger.log(logger.VERBOSE, f"{ctx.author} removed {role}", ctx.guild)
        # Remove role from DB and return if role existed in the DB in the first place;
        if dbfunctions.remove_role(ctx.guild.id, role):
            # Check for any guild members who still have this auto-role and remove it
            try:
                for member in ctx.guild.members:
                    if role in member.roles:
                        await member.remove_roles(role, reason="Automatic role update")
                        logger.log(logger.VERBOSE, f"removed auto from roles {member}", ctx.guild)
            # But if the bot cannot remove said roles...
            except Exception as e:
                logger.log(logger.ERROR, f"bot lacked authority level to remove {role} from people.", ctx.guild)


def setup(client):
    client.add_cog(Administration(client))
