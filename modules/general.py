import discord
from discord.ext import commands
from support.config import Config
from support.search import Search


class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.sniped_message = None

    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! ({round(self.client.latency * 1000)}ms)')

    @commands.command(aliases=['uinfo', 'ui'])
    async def userinfo(self, ctx, *, member = None):

        # Fetch relevant user and accompanying roles
        member = Search.search_user(ctx, member)
        roles = [role for role in member.roles]

        # Create embed
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
        # Set embed fields and values
        embed.set_author(name=f"{member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=Config.embed_footer, icon_url=self.client.user.avatar_url)

        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

        embed.add_field(name=f"Roles ({len(roles)}):", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="Top role:", value=member.top_role.mention)

        embed.add_field(name="Bot?", value=member.bot)
        await ctx.send(embed=embed)

    @commands.command(aliases=['sinfo', 'si'])
    async def serverinfo(self, ctx):
        # Set up
        roles = [role for role in ctx.guild.roles]
        roles.reverse()
        boosters = [booster for booster in ctx.guild.premium_subscribers]
        boosters.reverse()
        members_total = ctx.guild.members
        members_bots = sum(1 for member in members_total if member.bot is True)
        members_online = sum(1 for member in members_total if member.bot is False and member.status is not discord.Status.offline)
        members_offline = len(members_total) - members_bots - members_online

        # Create embed
        embed = discord.Embed(colour=self.client.user.color, timestamp=ctx.message.created_at)
        # Set embed defaults
        embed.set_author(name=f"{ctx.guild.name}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=Config.embed_footer, icon_url=self.client.user.avatar_url)

        # Set fields
        embed.add_field(name=f"Members: ({len(members_total)})", value=f"<:greendot:617798086403686432>{members_online} - <:reddot:617798085938118730>{members_offline} - 🤖 {members_bots}")
        embed.add_field(name="Created at:", value=ctx.guild.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name=f"Roles ({len(roles)}):", value=" ".join([role.mention for role in roles]))
        # Show nitro boosters
        if not boosters:
            embed.add_field(name=f"Nitro boosters (0)", value="None ")
        else:
            embed.add_field(name=f"Nitro boosters ({len(boosters)})", value=" ".join([booster.mention for booster in boosters]))
        await ctx.send(embed=embed)

    # Snipe command set up
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.sniped_message = message

    @commands.command()
    async def snipe(self, ctx):
        if self.sniped_message is None:
            await ctx.send("Nothing to be sniped.")
        else:
            embed = discord.Embed(colour=self.sniped_message.author.color, timestamp=self.sniped_message.created_at)
            embed.set_thumbnail(url=self.sniped_message.author.avatar_url)
            embed.set_footer(text=Config.embed_footer, icon_url=self.client.user.avatar_url)
            embed.add_field(name=f"{self.sniped_message.author} said:", value=self.sniped_message.content)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(General(client))
