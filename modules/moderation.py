import discord
from database import dbfunctions
from support import config as cfg
from discord.ext import commands
from support import services
from support import log
logger = log.Logger


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Make sure the moderator knows it worked!
    async def cog_after_invoke(self, ctx):
        try:
            await ctx.message.add_reaction(cfg.feedback_success_emoji_id)
        except Exception as e:
            # Only arrives here if message can't be found, i.e., using purge command.
            pass

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

    @commands.command(aliases=["nuke"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

    # Modify user statistics because they're cheating scum or something
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_activity(self, ctx, user: discord.Member, amount : int):
        if amount == 0: return
        if services.authority_check(user, ctx.author):
            dbfunctions.update_user_activity(ctx.guild, user, amount)
            logger.log(logger.VERBOSE, modification_text(ctx.author, user, amount, "activity points."), source=ctx.guild)
        else:
            await ctx.channel.send("Lacking authority to do this")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_message(self, ctx, user: discord.Member, amount : int):
        if amount == 0: return
        if services.authority_check(user, ctx.author):
            dbfunctions.update_user_messages(ctx.guild, user, amount)
            logger.log(logger.VERBOSE, modification_text(ctx.author, user, amount, "message count."), source=ctx.guild)
        else:
            await ctx.channel.send("Lacking authority to do this")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_karma(self, ctx, user: discord.Member, amount: int):
        if amount == 0: return
        if services.authority_check(user, ctx.author):
            dbfunctions.update_user_karma(ctx.guild, user, amount)
            logger.log(logger.VERBOSE, modification_text(ctx.author, user, amount, "karma."), source=ctx.guild)
        else:
            await ctx.channel.send("Lacking authority to do this")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def modify_tokens(self, ctx, user: discord.Member, amount: int):
        if amount == 0: return
        if services.authority_check(user, ctx.author):
            dbfunctions.update_user_tokens(ctx.guild, user, amount)
            logger.log(logger.VERBOSE, modification_text(ctx.author, user, amount, "tokens."), source=ctx.guild)
        else:
            await ctx.channel.send("Lacking authority to do this")


def modification_text(arg_user, arg_target_user, arg_amount, arg_modification_type):
    if arg_amount > 0:
        return f"{arg_user} added {arg_amount} to {arg_target_user}'s {arg_modification_type}"
    else:
        return f"{arg_user} removed {arg_amount} from {arg_target_user}'s {arg_modification_type}"


def setup(client):
    client.add_cog(Moderation(client))
