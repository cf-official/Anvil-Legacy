import discord
from discord.ext import commands
from support.bcolors import Bcolors
from emoji import UNICODE_EMOJI
from database import dbfunctions
from support import services


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Set custom prefix to guild
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, *, new_prefix):
        dbfunctions.set_guild_prefix(ctx.guild, new_prefix)
        await services.console_log(ctx.guild, Bcolors.MAGENTA, f"{ctx.author} changed the prefix to {new_prefix}")

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
            await services.console_log(ctx.guild, Bcolors.RED, f"{e}\nIn administration.py : set_karma_reaction")
        if emoji_id == "":
            await services.console_log(ctx.guild, Bcolors.RED,
                                       f"{ctx.guild} tried to set inaccesible emoji for karma reaction")
        else:
            dbfunctions.set_guild_karma_emoji(ctx.guild, emoji_id)
            await services.console_log(ctx.guild, Bcolors.MAGENTA, f"{ctx.author} set the karma emoji to {emoji_id}")

    # Set log_channel_id
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_log_channel_id(self, ctx, channel: discord.TextChannel = None):
        await services.console_log(ctx.guild, Bcolors.MAGENTA, f"{ctx.author} set logging channel to {channel}")
        if channel is None:
            dbfunctions.set_guild_log_channel(ctx.guild, None)
        else:
            dbfunctions.set_guild_log_channel(ctx.guild, channel.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_role(self, ctx, role: discord.Role, point_req=0, karma_req=0):
        await services.console_log(ctx.guild, Bcolors.MAGENTA,
                                   f"{ctx.author} added {role} with point req {point_req} and karma req {karma_req}")
        dbfunctions.add_role(ctx.guild.id, role, point_req, karma_req)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, role: discord.Role):
        await services.console_log(ctx.guild, Bcolors.MAGENTA, f"{ctx.author} removed {role}")
        # Remove role from DB and return if role existed in the DB in the first place;
        if dbfunctions.remove_role(ctx.guild.id, role):
            # Check for any guild members who still have this auto-role and remove it
            try:
                for member in ctx.guild.members:
                    if role in member.roles:
                        await member.remove_roles(role, reason="Automatic role update")
                        await services.console_log(ctx.guild, Bcolors.YELLOW, f"removed auto from roles {member}")
            # But if the bot cannot remove said roles...
            except Exception as e:
                await services.console_log(ctx.guild, Bcolors.RED,
                                           f"bot tried to remove the '{role}' role from guild members but lacked permissions to do so.")


def setup(client):
    client.add_cog(Administration(client))
