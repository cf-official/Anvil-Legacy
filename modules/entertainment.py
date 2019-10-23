from discord.ext import commands
import random


class Entertainment(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, question):
        responses = [   'It is certain',
                        'It is decidedly so',
                        'Without a doubt',
                        'Yes – definitely',
                        'You may rely on it',
                        'As I see it, yes',
                        'Most likely',
                        'Outlook is positive',
                        'Yes',
                        'Signs point to yes',

                        '*Reply unclear, try again*',
                        'Ask again later',
                        'Better not to tell you now',
                        'Cannot predict that right now',
                        'Concentrate and ask again',

                        'Don\'t count on it',
                        'My reply is no',
                        'My sources say no',
                        'Outlook isn\'t very good',
                        'Very doubtful']
        await ctx.send(f'Q: {question}\n'
                       f'A: {random.choice(responses)}')


def setup(client):
    client.add_cog(Entertainment(client))
