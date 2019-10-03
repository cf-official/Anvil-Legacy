import discord
from discord.ext import commands
from support.bcolors import Bcolors
from emoji import UNICODE_EMOJI
from database import dbfunctions


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Set custom prefix to guild
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, *, new_prefix):
        print(Bcolors.OKBLUE + f"{ctx.guild} prefix changed to {new_prefix}")

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
            print(Bcolors.FAIL + f"[Error] {e}\nIn administration.py : set_karma_reaction")
        if emoji_id == "":
            print(Bcolors.FAIL + f"[Error] {ctx.guild} tried to set inaccesible emoji for karma reaction")
        else:
            dbfunctions.set_guild_karma_emoji(ctx.guild, emoji_id)
            print(Bcolors.OKBLUE + f"{ctx.guild} karma emoji set to {emoji_id}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_role(self, ctx, role: discord.Role, point_req=0, karma_req=0):
        print(f"{ctx.guild}: {ctx.author} added {role} with point req {point_req} and karma req {karma_req}")
        dbfunctions.add_role(ctx.guild.id, role, point_req, karma_req)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_role(self,ctx, role: discord.Role):
        print(f"{ctx.guild}: {ctx.author} removed {role}")
        dbfunctions.remove_role(ctx.guild.id, role)

        # Check for any guild members who still have this auto-role and remove it
        for member in ctx.guild.members:
            if role in member.roles:
                await member.remove_roles(role, reason="Automatic role update")


def setup(client):
    client.add_cog(Administration(client))
