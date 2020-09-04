from discord.ext import commands
from database import dbfunctions
from support import services
from support.services import Search
import discord
import random
import math

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["share"])
    async def give(self, ctx, receiver=None, amount=None):
        # Require user input
        if not amount:
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, you did not specify an amount!")
            await services.failed_command_react(ctx.message)
            return

        sender_tokens = int(dbfunctions.get_user(ctx.author).tokens)

        # Parse amount
        amount = services.parse_amount(amount, sender_tokens)

        # Return any errors occurred while parsing
        if isinstance(amount, Exception):
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, {str(amount)}")
            await services.failed_command_react(ctx.message)
            return

        # Get receiver
        receiver_user = Search.search_user(ctx, receiver)

        # Safety checks
        if receiver_user is None:
            await services.send_simple_embed(ctx, ctx.author, f"I couldn't find any user from: ``{str(receiver)}``")
            await services.failed_command_react(ctx.message)
            return
        elif receiver_user.id is ctx.author.id:
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, you can't give tokens to yourself, smh!")
            await services.failed_command_react(ctx.message)
            return
        elif receiver_user.bot:
            await services.send_simple_embed(ctx, ctx.author, f"You can't give tokens to a bot, smh {ctx.author.mention}!")
            await services.failed_command_react(ctx.message)
            return

        # Update tokens
        dbfunctions.update_user_tokens(ctx.guild, ctx.author, amount * -1)
        dbfunctions.update_user_tokens(ctx.guild, receiver_user, amount)

        # Send success message
        await services.send_simple_embed(ctx, self.client.user, f"{ctx.author.mention} gave {receiver_user.mention} {abs(amount)} tokens.")

    @commands.command(aliases=["g", "gamba"])
    async def gamble(self, ctx, amount=None):
        # Require user input
        if not amount:
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, you did not specify an amount!")
            await services.failed_command_react(ctx.message)
            return

        user_tokens = int(dbfunctions.get_user(ctx.author).tokens)

        # Parse amount
        amount = services.parse_amount(amount, user_tokens)

        # Return any errors occurred while parsing
        if isinstance(amount, Exception):
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, {str(amount)}")
            await services.failed_command_react(ctx.message)
            return

        # Do the gamble and format user feedback
        roll = services.attempt_chance(1, 100, 49)
        result = "won" if roll[0] else "lost"
        if not roll[0]: amount = amount * -1
        result_text = f"{ctx.author.mention} {result} {abs(amount)} tokens and now has {user_tokens + amount}."

        # Update tokens and send user feedback
        dbfunctions.update_user_tokens(ctx.guild, ctx.author, amount)
        await services.send_simple_embed(ctx, self.client.user, result_text)

    @commands.command(aliases=["d", "die", "dice", "diceroll"])
    async def roll(self, ctx, amount=None):
        # Require user input
        if not amount:
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, you did not specify an amount!")
            await services.failed_command_react(ctx.message)
            return

        user_tokens = int(dbfunctions.get_user(ctx.author).tokens)

        # Parse amount
        amount = services.parse_amount(amount, user_tokens)

        # Return any errors occurred while parsing
        if isinstance(amount, Exception):
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, {str(amount)}")
            await services.failed_command_react(ctx.message)
            return

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        embed = discord.Embed()

        if user_roll == bot_roll:
            embed = discord.Embed(colour=discord.Color.from_rgb(243, 188, 64),
                               title="\\🎲 Die Roll - Tie!",
                               description=f"{ctx.author.mention} rolled the die and tied with {self.client.user.mention}!\nNo one lost any tokens!")

        elif user_roll < bot_roll:
            embed = discord.Embed(colour=discord.Color.from_rgb(241, 85, 74),
                               title="\\🎲 Die Roll - Lost!",
                               description=f"{ctx.author.mention} rolled the die and lost {abs(amount)} tokens to {self.client.user.mention}!")
            dbfunctions.update_user_tokens(ctx.guild, ctx.author, amount * -1)

        elif user_roll > bot_roll:
            embed = discord.Embed(colour=discord.Color.from_rgb(73, 230, 103),
                               title="\\🎲 Die Roll - Won!",
                               description=f"{ctx.author.mention} rolled the die against {self.client.user.mention} and won {abs(amount)} tokens!")
            dbfunctions.update_user_tokens(ctx.guild, ctx.author, amount)

        embed.add_field(name=f"{ctx.author.name}'s roll", value=f"``{user_roll}``")
        embed.add_field(name=f"{self.client.user.name}'s roll", value=f"``{bot_roll}``")

        await ctx.send(embed=embed)

    @commands.command(aliases=["b"])
    async def bet(self, ctx, face: int, amount=None):
        # Require user input
        if not face:
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, you did not specify a die face!")
            await services.failed_command_react(ctx.message)
            return
        elif face < 1 or face > 6:
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, a die only has 6 faces!")
            await services.failed_command_react(ctx.message)
            return

        if not amount:
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, you did not specify an amount!")
            await services.failed_command_react(ctx.message)
            return

        user_tokens = int(dbfunctions.get_user(ctx.author).tokens)

        # Parse amount
        amount = services.parse_amount(amount, user_tokens)

        # Return any errors occurred while parsing
        if isinstance(amount, Exception):
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, {str(amount)}")
            await services.failed_command_react(ctx.message)
            return

        if (amount < 20):
            await services.send_simple_embed(ctx, ctx.author, f"{ctx.author.mention}, you must bet at least 20 tokens!")
            await services.failed_command_react(ctx.message)
            return

        die_roll = random.randint(1, 6)

        embed = discord.Embed()

        if die_roll == face:
            random_multi = random.randint(500, 575)
            winnings = math.floor(amount / 100 * int(random_multi))

            dbfunctions.update_user_tokens(ctx.guild, ctx.author, winnings)

            embed = discord.Embed(colour=discord.Color.from_rgb(73, 230, 103),
                               title="\\🎲 Bet - Won!",
                               description=f"{ctx.author.mention} bet on ``{face}`` and won ``{winnings}`` tokens with a random multiplier of ``{abs(random_multi)}%``!")
        else:
            dbfunctions.update_user_tokens(ctx.guild, ctx.author, amount * -1)

            embed = discord.Embed(colour=discord.Color.from_rgb(241, 85, 74),
                               title="\\🎲 Bet - Lost!",
                               description=f"{ctx.author.mention} bet on ``{face}`` and lost ``{amount}`` tokens!")

        embed.add_field(name="Die roll", value=f"``{die_roll}``")

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Economy(client))
