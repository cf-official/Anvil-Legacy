import copy
import io
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import Optional
import discord
from discord.ext import commands
from support import config as cfg
from support import log
from support import services
from database import dbfunctions
logger = log.Logger

# Parts of this module were taken from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py

class GlobalChannel(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            # Not found... so fall back to ID + global lookup
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
                return channel

class BotAdmin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._last_result = None

    # Make sure only the owner can use this cog's commands
    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    def cleanup_code(self, content):
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            content = content[3:-3]
        if content.startswith('py'):
            content = content[2:]
        elif content.startswith('python'):
            content = content[6:]
        return content

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    # Loading modules
    @commands.command(hidden=True)
    async def load(self, ctx, *, extension):
        extension = extension.lower()
        try:
            self.client.load_extension(f'modules.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
            await ctx.message.add_reaction(cfg.feedback_error_emoji_id)
        else:
            logger.log(logger.DEBUG, f"Loaded the module \"{extension}\".")
            await ctx.message.add_reaction(cfg.feedback_success_emoji_id)

    # Unloading modules
    @commands.command(hidden=True)
    async def unload(self, ctx, *, extension):
        extension = extension.lower()
        try:
            self.client.unload_extension(f'modules.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
            await ctx.message.add_reaction(cfg.feedback_error_emoji_id)
        else:
            logger.log(logger.DEBUG, f"Unloaded the module \"{extension}\".")
            await ctx.message.add_reaction(cfg.feedback_success_emoji_id)

    # Reloading modules
    @commands.command(hidden=True)
    async def reload(self, ctx, *, extension):
        extension = extension.lower()
        try:
            self.client.reload_extension(f'modules.{extension}')
        except commands.ExtensionNotLoaded:
            self.client.load_extension(f'modules.{extension}')
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
            await ctx.message.add_reaction(cfg.feedback_error_emoji_id)
        else:
            logger.log(logger.DEBUG, f"Reloaded the module \"{extension}\".")
            await ctx.message.add_reaction(cfg.feedback_success_emoji_id)

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):

        env = {
            'client': self.client,
            'bot': self.client,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'services': services,
            'dbfunctions': dbfunctions,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await ctx.message.add_reaction(cfg.feedback_error_emoji_id)

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            await ctx.message.add_reaction(cfg.feedback_error_emoji_id)
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
            await ctx.message.add_reaction(cfg.feedback_success_emoji_id)

    @commands.command(hidden=True)
    async def sudo(self, ctx, channel: Optional[GlobalChannel], who: discord.User, *, command: str):
        msg = copy.copy(ctx.message)
        channel = channel or ctx.channel
        msg.channel = channel
        msg.author = channel.guild.get_member(who.id) or who
        msg.content = ctx.prefix + command
        try:
            new_ctx = await self.client.get_context(msg, cls=type(ctx))
            await self.client.invoke(new_ctx)
        except Exception as e:
            await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await ctx.message.add_reaction(cfg.feedback_error_emoji_id)
        else:
            await ctx.message.add_reaction(cfg.feedback_success_emoji_id)

def setup(client):
    client.add_cog(BotAdmin(client))
