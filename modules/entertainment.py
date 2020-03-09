from discord.ext import commands
from database import dbfunctions
from support import services
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
        message = f'Q: {question}\nA: {random.choice(responses)}'
        await services.send_simple_embed(ctx, self.client.user, message)

    @commands.command()
    async def gamble(self, ctx, amount):
        # Check if var amount is number, and if so if user has said number in tokens.
        user_tokens = dbfunctions.get_user(ctx.author).tokens

        # If not number, check if 'max' or 'half', gamble with that amount of tokens.
        if services.check_for_int(amount):
            if user_tokens < int(amount):
                # Fail the command
                await services.failed_command_react(ctx.message)
                return
        elif amount == "max":
            amount = user_tokens
        elif amount == "half":
            amount = round(user_tokens/2)
        else:
            # Fail the command
            await services.failed_command_react(ctx.message)
            return

        # Actually do the gambling here
        roll = services.attempt_chance(100, 55)
        amount = int(amount)
        if amount <= 0:
            # Fail the command
            await services.failed_command_react(ctx.message)
            return
        if roll[0]:
            # win
            result_text = f"{ctx.author} gambled {amount} tokens and won."
            # Different modifiers for winning here?
            # amount *= ?
        else:
            # lose
            result_text = f"{ctx.author} gambled {amount} tokens and lost."
            amount = amount * -1

        dbfunctions.update_user_tokens(ctx.guild, ctx.author, amount)
        await services.send_simple_embed(ctx, self.client.user, result_text)


def setup(client):
    client.add_cog(Entertainment(client))
