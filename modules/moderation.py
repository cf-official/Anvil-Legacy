import discord
from discord.ext import commands
from support.bcolors import Bcolors

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Kick/Ban/Unban
    @commands.command()
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        print(Bcolors.WARNING + f"{ctx.author} kicked {member}\nReason: {reason}")
        await member.kick(reason=reason)

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        print(Bcolors.WARNING + f"{ctx.author} banned {member}\nReason: {reason}")
        await member.ban(reason=reason)

    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                print(Bcolors.WARNING + f"{ctx.author} unbanned {member}")
                await ctx.guild.unban(user)
                return

    @commands.command()
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)


def setup(client):
    client.add_cog(Moderation(client))

"""
@client.event
async def on_ready():
    print('Bot is ready')



@client.event
async def on_member_remove(member):
    print(f'{member} has left the server')

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = [   'It is certain',
                    'It is decidedly so',
                    'Without a doubt',
                    'Yes – definitely',
                    'You may rely on it',
                    'As I see it, yes',
                    'Most likely',
                    'Outlook good',
                    'Yes',
                    'Signs point to yes',

                    ',Reply hazy, try again',
                    'Ask again later',
                    'Better not tell you now',
                    'Cannot predict now',
                    'Concentrate and ask again',

                    'Don\'t count on it',
                    'My reply is no',
                    'My sources say no',
                    ',Outlook not so good',
                    'Very doubtful']
    await ctx.send(f'Q: {question}\n'
                   f'A: {random.choice(responses)}')






"""
