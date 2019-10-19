import discord
from database import dbfunctions
from discord.ext import commands
from support import services
from support import log
logger = log.Logger


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Kick a user
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        if services.authority_check(user, ctx.author):
            logger.log(logger.VERBOSE, f"{ctx.author} kicked {user}.", ctx.guild)
            await user.kick(reason=reason)
        else:
            await ctx.channel.send("Lacking authority to do this")

    # Ban a user
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        if services.authority_check(user, ctx.author):
            logger.log(logger.VERBOSE, f"{ctx.author} banned {user}.", ctx.guild)
            await user.ban(reason=reason)
        else:
            await ctx.channel.send("Lacking authority to do this")

    # Un-ban a user
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = user.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                logger.log(logger.VERBOSE, f"{ctx.author} unbanned {user}", ctx.guild)
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
        if services.authority_check(user, ctx.author):
            dbfunctions.update_user_activity(ctx.guild, user, amount)
        else:
            await ctx.channel.send("Lacking authority to do this")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_message(self, ctx, user: discord.User, amount : int):
        if services.authority_check(user, ctx.author):
            dbfunctions.update_user_messages(ctx.guild, user, amount)
        else:
            await ctx.channel.send("Lacking authority to do this")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_karma(self, ctx, user: discord.User, amount : int):
        if services.authority_check(user, ctx.author):
            dbfunctions.update_user_karma(ctx.guild, user, amount)
        else:
            await ctx.channel.send("Lacking authority to do this")


def setup(client):
    client.add_cog(Moderation(client))
