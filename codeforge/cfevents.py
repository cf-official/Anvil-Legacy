import discord
from discord.ext import commands
from support.bcolors import Bcolors
from support import services
from support import config as cfg
from database import dbfunctions


# Check if the guild in question if CodeForge
def check_cf_guild(guild_id):
    if guild_id is cfg.cf_id:
        return True
    else:
        return False


# Member interaction (on_member_join event can't have multiple instances, hence this function)
async def cf_on_member_join(member):
    # Check if CF
    CF = member.guild
    if not check_cf_guild(CF.id): return
    # Manage newly added bots
    if member.bot is True:
        await services.console_log(member.guild, Bcolors.LIGHT_BLUE, f"{member} (bot) joined.")
        bot_role = [role for role in CF.roles if role.name == "bot"]
        await member.add_roles(bot_role)


class CFEvents(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(CFEvents(client))
