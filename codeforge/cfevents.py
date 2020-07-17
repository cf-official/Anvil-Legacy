from support import config as cfg
from codeforge import cfconfig as cfcfg
from discord.ext import commands
from support import log

logger = log.Logger


# Check if the guild in question if CodeForge
def check_cf_guild(guild_id):
    if guild_id == cfg.cf_id:
        return True
    else:
        return False


# Member interaction (on_member_join event can't have multiple instances, hence this function)
async def cf_on_member_join(member):
    # Check if CF
    cf = member.guild
    if not check_cf_guild(cf.id): return
    # Manage newly added bots
    if member.bot is True:
        logger.log(logger.VERBOSE, f"{member} (bot) joined.")
        bot_role = cf.get_role(cfcfg.bot_role_id)
        await member.add_roles(bot_role)


# Message handler specifically for integrating with CodeForge only features
# such as the present yourself lockout feature.
async def cf_on_message_create(message):
    # Check if CF
    cf = message.guild
    if not check_cf_guild(cf.id): return
    # Check if channel matches the stored id for #present-yourself
    if message.channel.id == cfcfg.present_channel_id:
        logger.log(logger.VERBOSE, f"{message.author} has introduced themselves, role applied", message.guild.name)
        member = cf.get_member(message.author.id)
        bot_role = cf.get_role(cfcfg.present_channel_role_id)
        await member.add_roles(bot_role[0])


class CFEvents(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(CFEvents(client))
