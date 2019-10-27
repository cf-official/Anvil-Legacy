from database.dbbase import Session
from database.guilds import Guild
from database.users import User
from database.roles import Role
from database.channels import Channel
from database.karma import KarmaEvents
from sqlalchemy import asc, desc
from support import services
from datetime import datetime
from support import services


# Guild updates
def guild_add(arg_guild):
    session = Session()
    guilds = session.query(Guild).all()
    # If new guild
    if sum(str(x.guild_id) == str(arg_guild.id) for x in guilds) is 0:
        new_guild = Guild(arg_guild.name, arg_guild.id)
        session.add(new_guild)
    # If guild still attached (Matched against bot id)
    elif sum(int(x.id) == 607163424362856458 for x in arg_guild.members) is 1:
        guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
        guild.attached = True
    # If guild left while bot offline
    else:
        guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
        guild.attached = False
    session.commit()
    session.close()


# Mark guild as detached from bot in db
def guild_remove(arg_guild):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    guild.attached = False
    session.commit()
    session.close()


# Fetch user from db and return all data that belongs to user
def retrieve_guild(arg_guild):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    dbguild = services.AttrDict()
    dbguild.update({"name": guild.name, "id": guild.guild_id, "join_date": guild.join_date, "prefix": guild.prefix,
                    "attached": guild.attached, "karma_emoji": guild.karma_emoji,
                    "log_channel_id": guild.log_channel_id})
    session.commit()
    session.close()
    return dbguild


# Fetch the current possibly custom guild prefix
def get_guild_prefix(arg_guild):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    prefix = guild.prefix
    session.commit()
    session.close()
    return prefix


# Set new guild prefix
def set_guild_prefix(arg_guild, arg_prefix):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    guild.prefix = arg_prefix
    session.commit()
    session.close()


# Set chosen reaction emoji for karma system
def set_guild_karma_emoji(arg_guild, arg_emoji_id):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    guild.karma_emoji = arg_emoji_id
    session.commit()
    session.close()


# Set chosen channel ID for logging channel
def set_guild_log_channel(arg_guild, arg_channel_id):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    guild.log_channel_id = arg_channel_id
    session.commit()
    session.close()


# Add new users to DB, works both on build and on_guild_join
def guild_add_users(arg_guild):
    # Prep session
    session = Session()
    users = arg_guild.members
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    # Create new users and add them to guild
    for user in users:
        if not user.bot:
            # Check if user already exists for guild
            if sum(str(x.user_id) == str(user.id) for x in guild.users) is 0:
                new_user = User(user.name, user.id)
                guild.users.append(new_user)
                session.add(new_user)
    session.commit()
    session.close()


# Add a single user to DB
def add_user(arg_guild, arg_user):
    # Prep session
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    new_user = User(arg_user.name, arg_user.id)
    guild.users.append(new_user)
    session.add(new_user)
    session.commit()
    session.close()


# Updates amount of messages stored in DB based on arg: increment
def update_user_messages(arg_guild, arg_user, arg_increment):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(arg_user.id)), None)
    user.messages_sent += arg_increment
    session.commit()
    session.close()


# Updates amount of activity points stored in DB based on arg: increment
def update_user_activity(arg_guild, arg_user, arg_increment):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(arg_user.id)), None)
    user.activity_points += arg_increment
    user.last_message = datetime.now()
    session.commit()
    session.close()


# Updates amount of karma stored in DB based on arg: increment
def update_user_karma(arg_guild, arg_user, arg_increment):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(arg_user.id)), None)
    user.karma += arg_increment
    session.commit()
    session.close()


# Updates amount of tokens stored in DB based on arg: increment
def update_user_tokens(arg_guild, arg_user, arg_increment):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(arg_user.id)), None)
    user.tokens += arg_increment
    session.commit()
    session.close()


# Store karma giving event with required datetime
def set_karma_event(arg_channel, arg_user_giving, arg_user_receiving, arg_guild_id):
    session = Session()
    # Retrieve required data
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    giving_user = next((x for x in guild.users if int(x.user_id) == int(arg_user_giving.id)), None)
    receiving_user = next((x for x in guild.users if int(x.user_id) == int(arg_user_receiving.id)), None)

    # Check if pre-existing matching karma event
    event_check = session.query(KarmaEvents).filter(
        (KarmaEvents.user_giving_id == giving_user.id) & (KarmaEvents.user_receiving_id == receiving_user.id)).order_by(
        desc(KarmaEvents.datetime)).first()
    if event_check:
        # The event already exists, check datetime
        if event_check.datetime != datetime.today().date():
            session.add(KarmaEvents(giving_user.id, receiving_user.id, arg_channel.id))
            check = True
        else:
            check = False
    else:
        # The event doesn't exist, make a new one!
        session.add(KarmaEvents(giving_user.id, receiving_user.id, arg_channel.id, ))
        check = True
    session.commit()
    session.close()
    return check


# Fetch user from db and return all data that belongs to user
def retrieve_user(arg_user):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_user.guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(arg_user.id)), None)
    dbuser = services.AttrDict()
    dbuser.update({"name" : user.name, "user_id": user.user_id, "messages_sent": user.messages_sent,
                   "activity_points": user.activity_points, "tokens": user.tokens, "karma": user.karma,
                   "last_message": user.last_message})
    session.commit()
    session.close()
    return dbuser


# Check if last message exists and match datetimes against it
def check_user_last_message(arg_user, arg_guild_id):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(arg_user.id)), None)
    if user.last_message is None:
        user.last_message = datetime.now()
    if services.difference_in_minutes(user.last_message, datetime.now()) > 1:
        user.last_message = datetime.now()
        result = True
    else:
        result = False
    session.commit()
    session.close()
    return result


# Check if used reaction is the guild karma reaction
def check_reaction(arg_emoji_id, arg_guild_id):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()

    # Return if the reaction matches true or false
    if guild.karma_emoji == arg_emoji_id:
        return True
    else:
        return False


# Add roles to the autorole list, with required conditions
def add_role(arg_guild_id, arg_role, arg_message_req, arg_point_req, arg_karma_req, arg_token_req):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    # Check if role already exists for guild
    if sum(str(x.role_id) == str(arg_role.id) for x in guild.roles) is 0:
        # Create new role object for db
        new_role = Role(arg_role.id, arg_message_req, arg_point_req, arg_karma_req, arg_token_req)
        guild.roles.append(new_role)
        session.add(new_role)
    session.commit()
    session.close()


# Grab all role objects belonging to guild and return them as a list
def retrieve_roles(arg_guild_id):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    roles = guild.roles.copy()
    session.close()
    return roles


# Remove autorole for guild
def remove_role(arg_guild_id, arg_role):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    # Fetch role through guild
    role_to_remove = next((x for x in guild.roles if int(x.role_id) == int(arg_role.id)), None)
    if role_to_remove is not None:
        guild.roles.remove(role_to_remove)
        session.delete(role_to_remove)
    else:
        session.close()
        return False
    session.commit()
    session.close()
    return True


# Retrieve all top 10 users per stat from guild
def retrieve_top_users(arg_guild):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild.id).first()

    # Fetch top 10 users for the 4 attributes; messages/acitivity/karma/tokens
    top_messages, top_activity, top_karma, top_tokens = [], [], [], []
    # Fetch top messages_sent
    temp_list = sorted(guild.users, key=lambda x: x.messages_sent, reverse=True)[:10]
    for x in temp_list:
        guild_user = arg_guild.get_member(int(x.user_id))
        dbuser = services.AttrDict()
        dbuser.update({"name": str(guild_user.display_name), "messages_sent": x.messages_sent})
        top_messages.append(dbuser)
    # Fetch top activity points
    temp_list = sorted(guild.users, key=lambda x: x.activity_points, reverse=True)[:10]
    for x in temp_list:
        guild_user = arg_guild.get_member(int(x.user_id))
        dbuser = services.AttrDict()
        dbuser.update({"name": str(guild_user.display_name), "activity_points": x.activity_points})
        top_activity.append(dbuser)
    # Fetch top karma
    temp_list = sorted(guild.users, key=lambda x: x.karma, reverse=True)[:10]
    for x in temp_list:
        guild_user = arg_guild.get_member(int(x.user_id))
        dbuser = services.AttrDict()
        dbuser.update({"name": str(guild_user.display_name), "karma": x.karma})
        top_karma.append(dbuser)
    # Fetch top karma
    temp_list = sorted(guild.users, key=lambda x: x.tokens, reverse=True)[:10]
    for x in temp_list:
        guild_user = arg_guild.get_member(int(x.user_id))
        dbuser = services.AttrDict()
        dbuser.update({"name": str(guild_user.display_name), "tokens": x.tokens})
        top_tokens.append(dbuser)
    dbresults = services.AttrDict()
    dbresults.update({"top_messages": top_messages, "top_activity": top_activity,
                      "top_karma": top_karma, "top_tokens": top_tokens})
    session.commit()
    session.close()
    return dbresults


# Add channels to the set of channels where bot commands are allowed
def add_channel(arg_guild_id, arg_channel):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    # Check if channel already exists for guild
    if sum(str(x.channel_id) == str(arg_channel.id) for x in guild.channels) is 0:
        # Create new channel object for db
        new_channel = Channel(arg_channel.id)
        guild.channels.append(new_channel)
        session.add(new_channel)
    session.commit()
    session.close()


# Remove bot commands channel for guild
def remove_channel(arg_guild_id, arg_channel):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    # Fetch channel through guild
    channel_to_remove = next((x for x in guild.channels if int(x.channel_id) == int(arg_channel.id)), None)
    if channel_to_remove is not None:
        guild.channels.remove(channel_to_remove)
        session.delete(channel_to_remove)
    session.commit()
    session.close()


# Retrieve all bot commands channels
def retrieve_channels(arg_guild_id):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    channels = guild.channels.copy()
    session.close()
    return channels
