
from database import dbfunctions
from datetime import datetime
from support import config as cfg
import random
import operator
import time
import re
from support import log
logger = log.Logger
from discord.ext import commands


# Search for a specific user and return it
class Search:
    @staticmethod
    def search_user(ctx, search):
        # Search by discord user
        user = next((i for i in ctx.guild.members if str(search).lower() in str(i).lower()), None)
        # Search by discord user nickname
        if user is None:
            user = next((i for i in ctx.guild.members if str(search).lower() in str(i.display_name).lower()), None)
        # Search discord by id
        if user is None and search is not None:
            # Remove all non-numerics
            search = re.sub("[^0-9]", "", search)
            user = next((i for i in ctx.guild.members if search.lower() in str(i.id)), ctx.author)
        elif search is None:
            user = ctx.author
        return user


# Allows for creation of a dict that allows attributes to be called instead of keys
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def difference_in_minutes(d1, d2):
    # Convert to Unix timestamp
    d1_ts = time.mktime(d1.timetuple())
    d2_ts = time.mktime(d2.timetuple())

    # They are now in seconds, subtract and then divide by 60 to get minutes.
    difference = int(d2_ts - d1_ts) / 60
    return difference


def get_roles_by_id(guild, list_roles_id):
    list_roles_objects = []
    for role in list_roles_id:
        # Create role dict with attributes after fetching role object
        x = guild.get_role(int(role.role_id))
        dbrole = AttrDict()
        dbrole.update({"role": x, "message_req": role.message_requirement,"point_req": role.point_requirement,
                       "karma_req": role.karma_requirement, "token_req": role.token_requirement})
        # Add role dict to list
        list_roles_objects.append(dbrole)
    list_roles_objects = sorted(list_roles_objects, key=operator.itemgetter('point_req', 'message_req',
                                                                            'karma_req', 'token_req'), reverse=True)
    return list_roles_objects


def get_channels_by_id(guild, list_channels_id):
    list_channels_objects = []
    for channel in list_channels_id:
        # Create role dict with attributes after fetching role object
        x = guild.get_channel(int(channel.channel_id))
        # Add role dict to list
        list_channels_objects.append(x)
    return list_channels_objects


async def set_user_auto_roles(user, guild):
    # Auto role and user data
    roles_raw = dbfunctions.retrieve_roles(guild.id)
    auto_roles = get_roles_by_id(guild, roles_raw)

    user_data = dbfunctions.retrieve_user(user)
    user_messages, user_points, user_karma, user_tokens = user_data.messages_sent, \
                                                          user_data.activity_points, user_data.karma, user_data.tokens
    # Role lists
    all_auto_roles = []
    current_roles = user.roles
    allowed_roles = []
    not_allowed_roles = []

    # Check which auto_roles apply to the current user
    for role in auto_roles:
        all_auto_roles.append(role.role)
        if user_messages >= role.message_req and user_points >= role.point_req and user_karma >= role.karma_req \
                and user_tokens >= role.token_req:
            allowed_roles.append(role.role)

    # Remove auto roles the user shouldn't have from current_roles
    for role in current_roles.copy():
        if role in all_auto_roles and role not in allowed_roles:
            not_allowed_roles.append(role)
        if role not in allowed_roles:
            current_roles.remove(role)

    # Set up roles to actually add
    for role in allowed_roles.copy():
        if role in current_roles:
            allowed_roles.remove(role)

    # Actually add/remove roles here
    # Add roles first. Might break if missing required perms!
    if bool(allowed_roles):
        try:
            await user.add_roles(*allowed_roles, reason="Automatic role update")
            logger.log(logger.INFO, f"added auto roles to {user}", guild)
        except Exception as e:
            logger.log(logger.ERROR, f"couldn't add an auto role to {user} due to: {e}.", guild)
    # Removed roles. Might break if missing required perms!
    if bool(not_allowed_roles):
        try:
            await user.remove_roles(*not_allowed_roles, reason="Automatic role update")
            logger.log(logger.INFO, f"removed auto from roles {user}", guild)
        except Exception as e:
            logger.log(logger.ERROR, f"couldn't remove an auto role from {user} due to: {e}.", guild)


# Takes messages and prints them to the determined log channel in the guild (if it exists)
async def guild_log(arg_guild, arg_content, arg_error):
    # Time logging
    now = datetime.now()
    now_string = now.strftime("%d/%m/%Y %H:%M:%S")
    # Error logging
    if arg_error:
        arg_content += f"\n\nIn this error persists, please notify {cfg.owner}"
    # Fetch log-channel status, if returns true post to there
    guild_data = dbfunctions.retrieve_guild(arg_guild)
    if guild_data.log_channel_id:
        try:
            channel = arg_guild.get_channel(int(guild_data.log_channel_id))
            await channel.send(f"```ini\n[{now_string}]\n{arg_content}\n```")
        except Exception as e:
            logger.log(logger.ERROR, f"{e}", arg_guild)


# Check if user has higher authority level
def authority_check(arg_target_user, arg_user):
    if arg_user.top_role >= arg_target_user.top_role:
        return True
    else:
        return False


# Makes it so the top users are displayed properly (shortening of names and stuff)
def top_users_formatter(arg_list):
    new_list = []
    username_max_length = 20
    for x in arg_list:
        y = x.user
        if len(y) > username_max_length:
            y = y[:username_max_length]
        while len(y) < username_max_length:
            y += "."
        y += "....." + str(x.value)
        new_list.append(y)
    return new_list


# Calculate odds based on given max_odd, then attempt to win at those odds. Return True/False = Win/Loss
<<<<<<< Updated upstream
def attempt_chance(max_range, winning_range):
    roll = random.randrange(1, max_range+1)
=======
def attempt_chance(min_range, max_range, winning_range):
    roll = random.randrange(min_range, max_range+1)
>>>>>>> Stashed changes
    result = True if roll <= winning_range else False
    return result, roll


# React to a given message with a number, using numerical emoji...
async def numerical_reaction(message, number):
<<<<<<< Updated upstream
    numerical_emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    for x in str(number):
        await message.add_reaction(numerical_emoji_list[int(x)])
=======
    try:
        await message.add_reaction("💲")
        numerical_emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        for x in str(number):
            await message.add_reaction(numerical_emoji_list[int(x)])
    except Exception as e:
        logger.log(logger.VERBOSE, e, message.author.guild)


# Adds a 'failed' emoji to a message
async def failed_command_react(message):
    await message.add_reaction(cfg.feedback_error_emoji_id)


# Send a simple embed
async def send_simple_embed(ctx, user, text):
    embed = discord.Embed(colour=user.color, title=text)
    await ctx.send(embed=embed)


# Check if given input (perhaps a string), is a number
def is_int(variable):
    try:
        int(variable)
        return True
    except ValueError:
        return False
>>>>>>> Stashed changes
