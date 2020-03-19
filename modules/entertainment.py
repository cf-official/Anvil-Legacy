from discord.ext import commands
from database import dbfunctions
from support import services
import random
import math


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

        message = f'Q: {question}\nA: {random.choice(responses)}'
        await services.send_simple_embed(ctx, self.client.user, message)

    @commands.command(aliases=["g", "gamba"])
    async def gamble(self, ctx, amount=None):
        user_tokens = int(dbfunctions.get_user(ctx.author).tokens)

        # Require user input
        if not amount: raise Exception("No user input")

        # If input is not an int, determine amount
        if not services.is_int(amount):
            if amount == "half":
                amount = math.floor(user_tokens/2)
            elif amount in ["max", "all", "gamba"]:
                amount = user_tokens
            elif "%" in amount:
                amount = str(amount).replace("%", "")
                if not services.is_int(amount):
                    raise Exception("Bad user input")
                amount = math.floor(user_tokens/100 * int(amount))
            else:
                raise Exception("Bad user input")
        amount = int(amount)
        if 0 >= amount or amount > user_tokens: raise Exception("Faulty token amount")

        # Do the gamble and format user feedback
        roll = services.attempt_chance(1, 100, 49)
        result = "won" if roll[0] else "lost"
        result_text = f"{ctx.author.display_name} {result} {amount} tokens and now has {user_tokens + amount}."
        if not roll[0]: amount = amount * -1

        # Update tokens and send user feedback
        dbfunctions.update_user_tokens(ctx.guild, ctx.author, amount)
        await services.send_simple_embed(ctx, self.client.user, result_text)


def setup(client):
    client.add_cog(Entertainment(client))
