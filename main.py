import os
from discord.ext import commands
import time
from support import config as cfg
from support import services
from database.dbbase import initialize_sql
from database import dbfunctions
import sqlalchemy
from support import log
logger = log.Logger

# Initiate and/or prepare db & db tables
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + cfg.mysql['user'] + ':' + cfg.mysql['password'] + '@' + cfg.mysql['host'] + '/' + cfg.mysql['database']
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
initialize_sql(engine)


# Check custom guild prefix'
def get_prefix(client, message):
    guild_prefix = dbfunctions.get_guild_prefix(message.guild) if message.guild is not None else cfg.default_prefix
    prefix = [cfg.default_prefix, guild_prefix]
    return prefix


# Chosen prefix
client = commands.Bot(command_prefix=get_prefix)


# Loading modules
@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    extension = extension.lower()
    try:
        client.load_extension(f'modules.{extension}')
    except:
        logger.log(logger.ERROR, "Tried loading a module that either didn't exist or was already loaded")
    else:
        logger.log(logger.DEBUG, f"Loaded the module \"{extension}\".")


# Unloading modules
@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    extension = extension.lower()
    try:
        client.unload_extension(f'modules.{extension}')
    except:
        logger.log(logger.ERROR, "Tried unloading a module that either didn't exist or was already unloaded")
    else:
        logger.log(logger.DEBUG, f"Unloaded the module \"{extension}\".")

# Loading all available modules on startup
for filename in os.listdir('./modules'):
    if filename.endswith('.py'):
        client.load_extension(f'modules.{filename[:-3]}')

# Keep reconnecting forever if connection lost for whatever reason
sleep_timer = 5
while True:
    try:
        # Actually run client with key
        client.loop.run_until_complete(client.run(cfg.token))
        sleep_timer = 5
    except BaseException:
        logger.log(logger.ERROR, f'Waiting {sleep_timer} seconds before next reconnection attempt...')
        sleep_timer += 5
        time.sleep(sleep_timer)
