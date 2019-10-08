import discord
from database import dbfunctions
from discord.ext import commands
from support.bcolors import Bcolors
from support import services


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Kick a user
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member.guild_premissions.kick_members and not ctx.user.guild_permissions.administrator \
                and not member.guild_premissions.administrator:
            await ctx.send("Can't kick member with equal permission level!")
        services.console_log(ctx.guild, Bcolors.MAGENTA, f"{ctx.author} kicked {member}\nReason: {reason}")
        await member.kick(reason=reason)

    # Ban a user
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member.guild_premissions.ban_members and not ctx.user.guild_permissions.administrator \
                and not member.guild_premissions.administrator:
            await ctx.send("Can't kick member with equal permission level!")
        services.console_log(ctx.guild, Bcolors.MAGENTA, f"{ctx.author} banned {member}\nReason: {reason}")
        await member.ban(reason=reason)

    # Un-ban a user
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                services.console_log(ctx.guild, Bcolors.MAGENTA, f"{ctx.author} unbanned {member}")
                await ctx.guild.unban(user)
                return

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

    # Modify user statistics because they're cheating scum or something
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_activity(self, ctx, user: discord.User, amount : int):
        dbfunctions.update_user_activity(ctx.guild, user, amount)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_message(self, ctx, user: discord.User, amount : int):
        dbfunctions.update_user_messages(ctx.guild, user, amount)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_karma(self, ctx, user: discord.User, amount : int):
        dbfunctions.update_user_karma(ctx.guild, user, amount)


def setup(client):
    client.add_cog(Moderation(client))
