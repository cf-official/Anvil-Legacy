import discord
from discord.ext import commands
from support import config as cfg
from support.services import Search
from support import services
from database import dbfunctions
# from support import UIdrawer
import math
import random


class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! ({round(self.client.latency * 1000)}ms)')

    @commands.command(aliases=['uinfo', 'ui'])
    async def userinfo(self, ctx, *, user=None):
        # wait UIdrawer.request_ui_card()
        # await ctx.send(file=discord.File('support/uicard.png'))

        # Fetch relevant user and accompanying roles
        user = Search.search_user(ctx, user)
        roles = [role for role in user.roles]
        # Slice @@everyone out of the list
        roles = roles[1:]
        # Get user position in guild history (the Xth user to join the guild... that's still in the guild)
        position = sorted(ctx.guild.members, key=lambda x: x.joined_at).index(user) + 1
        ordinal = get_ordinal(position)

        # Create embed
        embed = discord.Embed(colour=user.color, timestamp=ctx.message.created_at, title="*Questions?*",
                              url=cfg.embed_url)
        # Set embed fields and values
        embed.set_author(name=f"{user}")
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=cfg.embed_footer, icon_url=self.client.user.avatar_url)

        embed.add_field(name="-",
                        value="**ID:** " + str(user.id) + "\n"
                                                          "**Created at:** " + user.created_at.strftime(
                            "%a, %#d %B %Y, %I:%M %p UTC") + "\n"
                                                             "**Joined at:** " + user.joined_at.strftime(
                            "%a, %#d %B %Y, %I:%M %p UTC") + "\n"
                                                             f"**{ordinal} member of {ctx.guild}.**", inline=False)

        # Make sure roles are listed correctly, even if empty
        if roles:
            embed.add_field(name=f"Roles ({len(roles)}):", value=" ".join([role.mention for role in roles]),
                            inline=False)
            embed.add_field(name="Top role:", value=user.top_role.mention, inline=True)
        else:
            embed.add_field(name="Roles (0):", value="None")
            embed.add_field(name="Top role:", value="None", inline=True)
        embed.add_field(name="Bot?", value=user.bot, inline=True)

        if not user.bot:
            dbuser = dbfunctions.get_user(user)
            embed.add_field(name="User involvement", value=":e_mail: Messages sent: " + str(
                dbuser.messages_sent) + " :speaking_head: Activity: " + str(dbuser.activity_points), inline=False)
            embed.add_field(name="User stats", value=":angel: Karma: " + str(dbuser.karma) +
                                                     " :moneybag: Tokens: " + str(dbuser.tokens), inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['sinfo', 'si'])
    async def serverinfo(self, ctx):
        # Set up
        roles = [role for role in ctx.guild.roles]
        roles.reverse()
        # Remove last role (@@everyone)
        roles = roles[:-1]

        boosters = [booster for booster in ctx.guild.premium_subscribers]
        boosters.reverse()
        members_total = ctx.guild.members
        members_bots = sum(1 for member in members_total if member.bot is True)
        members_online = sum(
            1 for member in members_total if member.bot is False and member.status is not discord.Status.offline)
        members_offline = len(members_total) - members_bots - members_online

        # Create embed
        embed = discord.Embed(colour=self.client.user.color, timestamp=ctx.message.created_at, title="*Questions?*",
                              url=cfg.embed_url)
        # Set embed defaults
        embed.set_author(name=f"{ctx.guild.name}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=cfg.embed_footer, icon_url=self.client.user.avatar_url)

        # Set fields
        embed.add_field(name=f"Members ({len(members_total)}): ",
                        value=f"<:greendot:617798086403686432>{members_online} - <:reddot:617798085938118730>{members_offline} - 🤖 {members_bots}",
                        inline=True)
        embed.add_field(name="Created at:", value=ctx.guild.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"),
                        inline=True)

        # Make sure roles are listed correctly, even if empty
        if roles:
            embed.add_field(name=f"Roles ({len(roles)}):", value=" ".join([role.mention for role in roles]),
                            inline=False)
        else:
            embed.add_field(name="Roles (0):", value="None", inline=False)

        # Show nitro boosters
        if not boosters:
            embed.add_field(name=f"Nitro boosters (0): ", value="None ")
        else:
            embed.add_field(name=f"Nitro boosters ({len(boosters)}): ",
                            value=" ".join([booster.mention for booster in boosters]))
        await ctx.send(embed=embed)

    @commands.command()
    async def roles(self, ctx):
        roles_raw = dbfunctions.retrieve_roles(ctx.guild.id)
        roles = services.get_roles_by_id(ctx.guild, roles_raw)
        roles_string = ""
        for role in roles:
            roles_string += role.role.mention
            if role.message_req > 0:
                roles_string += "\n Messages: " + str(role.message_req)
            if role.point_req > 0:
                roles_string += "\n Points: " + str(role.point_req)
            if role.karma_req > 0:
                roles_string += "\n Karma: " + str(role.karma_req)
            if role.token_req > 0:
                roles_string += "\n Tokens: " + str(role.token_req)
            roles_string += "\n\n"

        # Create embed
        embed = discord.Embed(colour=self.client.user.color, timestamp=ctx.message.created_at, title="*Questions?*",
                              url=cfg.embed_url)
        # Set embed defaults
        embed.set_author(name=f"{ctx.guild.name} - Role Requirements")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=cfg.embed_footer, icon_url=self.client.user.avatar_url)

        # Set fields
        embed.add_field(name=f"Roles({len(roles)}):", value=roles_string)
        await ctx.send(embed=embed)

    @commands.command(aliases=['lboard', 'lb'])
    async def leaderboard(self, ctx, lbtype=None):
        embed = discord.Embed(colour=self.client.user.color, timestamp=ctx.message.created_at, title="*Questions?*",
                              url=cfg.embed_url)
        embed.set_footer(text=cfg.embed_footer, icon_url=self.client.user.avatar_url)

        # Check if lbtype matches any, else post default leaderboard

        # Fetch top ten users based on messages
        if lbtype == "messages":
            header, results = dbfunctions.retrieve_top_messages(ctx.guild)
        elif lbtype == "activity":
            header, results = dbfunctions.retrieve_top_activity(ctx.guild)
        elif lbtype == "karma":
            header, results = dbfunctions.retrieve_top_karma(ctx.guild)
        elif lbtype == "tokens":
            header, results = dbfunctions.retrieve_top_tokens(ctx.guild)
        # No type, or invalid type, was given. Return embed with instructions
        else:
            embed.add_field(name="Leaderboard usage", value=".leaderboard messages\n"
                                                            ".leaderboard activity\n"
                                                            ".leaderboard karma\n"
                                                            ".leaderboard tokens")
            await ctx.send(embed=embed)
            return

        # Setup of actual embed text
        results = services.top_users_formatter(results)
        embed.add_field(name="Leaderboard - " + header, value="\n".join(
            [str(count) + ". " + x for count, x in enumerate(results, start=1)]), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, max=100):
        roll = random.randrange(0, max)
        await ctx.send(f"{ctx.author} rolled: {roll}")

    @commands.command(aliases=["k"])
    async def karma(self, ctx, user: discord.User=None):
        if user is not None:
            if not user.bot:
                user = Search.search_user(ctx, user)
                dbuser = dbfunctions.get_user(user)
                embed = discord.Embed(colour=user.color,
                                      url=cfg.embed_url)
                # Set embed fields and values
                embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
                embed.description = f":angel: Karma: {dbuser.karma}"
                await ctx.send(embed=embed)
        else:
            user = ctx.author
            dbuser = dbfunctions.get_user(ctx.author)
            embed = discord.Embed(colour=user.color,
                                  url=cfg.embed_url)
            # Set embed fields and values
            embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
            embed.description = f":angel: Karma: {dbuser.karma}"
            await ctx.send(embed=embed)

    @commands.command(aliases=["a"])
    async def activity(self, ctx, user: discord.User=None):
        if user is not None:
            if not user.bot:
                user = Search.search_user(ctx, user)
                dbuser = dbfunctions.get_user(user)
                embed = discord.Embed(colour=user.color,
                                      url=cfg.embed_url)
                # Set embed fields and values
                embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
                embed.description = f":e_mail: Activity: {dbuser.activity_points}"
                await ctx.send(embed=embed)
        else:
            user = ctx.author
            dbuser = dbfunctions.get_user(ctx.author)
            embed = discord.Embed(colour=user.color,
                                  url=cfg.embed_url)
            # Set embed fields and values
            embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
            embed.description = f":e_mail: Activity: {dbuser.activity_points}"
            await ctx.send(embed=embed)

    @commands.command(aliases=["to"])
    async def tokens(self, ctx, user: discord.User=None):
        if user is not None:
            if not user.bot:
                user = Search.search_user(ctx, user)
                dbuser = dbfunctions.get_user(user)
                embed = discord.Embed(colour=user.color,
                                      url=cfg.embed_url)
                # Set embed fields and values
                embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
                embed.description = f":moneybag: Tokens: {dbuser.tokens}"
                await ctx.send(embed=embed)
        else:
            user = ctx.author
            dbuser = dbfunctions.get_user(ctx.author)
            embed = discord.Embed(colour=user.color,
                                  url=cfg.embed_url)
            # Set embed fields and values
            embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
            embed.description = f":moneybag: Tokens: {dbuser.tokens}"
            await ctx.send(embed=embed)

    @commands.command(aliases=["me", "m"])
    async def messages(self, ctx, user: discord.User=None):
        if user is not None:
            if not user.bot:
                user = Search.search_user(ctx, user)
                dbuser = dbfunctions.get_user(user)
                embed = discord.Embed(colour=user.color,
                                      url=cfg.embed_url)
                # Set embed fields and values
                embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
                embed.description = f":speaking_head: Messages: {dbuser.messages_sent}"
                await ctx.send(embed=embed)
        else:
            user = ctx.author
            dbuser = dbfunctions.get_user(ctx.author)
            embed = discord.Embed(colour=user.color,
                                  url=cfg.embed_url)
            # Set embed fields and values
            embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
            embed.description = f":speaking_head: Messages: {dbuser.messages_sent}"
            await ctx.send(embed=embed)

def get_ordinal(number):
    ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])
    result = ordinal(number)
    return result


def setup(client):
    client.add_cog(General(client))
