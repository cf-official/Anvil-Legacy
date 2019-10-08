from database.dbbase import Session
from database.guilds import Guild
from database.users import User
from database.roles import Role
from database.karma import KarmaEvents
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


# Store karma giving event with required datetime
def set_karma_event(arg_user_giving, arg_user_receiving, arg_guild_id):
    session = Session()

    # Retrieve required data
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    giving_user = next((x for x in guild.users if int(x.user_id) == int(arg_user_giving.id)), None)
    receiving_user = next((x for x in guild.users if int(x.user_id) == int(arg_user_receiving.id)), None)

    # Check if pre-existing matching karma event
    event_check = session.query(KarmaEvents).filter((KarmaEvents.user_giving_id == giving_user.id) &
                                                    (KarmaEvents.user_receiving_id == receiving_user.id)).first()
    if event_check:
        # The event already exists, check datetime
        if event_check.datetime != datetime.today().date():
            event_check.datetime = datetime.today().date()
            check = True
        else:
            check = False
    else:
        # The event doesn't exist, make a new one!
        session.add(KarmaEvents(giving_user.id, receiving_user.id, datetime.today().date()))
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
def add_role(arg_guild_id, arg_role, arg_point_req, arg_karma_req):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()
    # Check if role already exists for guild
    if sum(str(x.role_id) == str(arg_role.id) for x in guild.roles) is 0:
        # Create new role object for db
        new_role = Role(arg_role.id, arg_point_req, arg_karma_req)
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
    session.commit()
    session.close()


# Retrieve all top 10 users per stat from guild
def retrieve_top_users(arg_guild_id):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == arg_guild_id).first()

    # Fetch top 10 users for the 4 attributes; messages/acitivity/karma/tokens
    top_messages, top_activity, top_karma, top_tokens = [], [], [], []
    # Fetch top messages_sent
    temp_list = sorted(guild.users, key=lambda x: x.messages_sent, reverse=True)[:10]
    for x in temp_list:
        dbuser = services.AttrDict()
        dbuser.update({"name": x.name, "messages_sent": x.messages_sent})
        top_messages.append(dbuser)
    # Fetch top activity points
    temp_list = sorted(guild.users, key=lambda x: x.activity_points, reverse=True)[:10]
    for x in temp_list:
        dbuser = services.AttrDict()
        dbuser.update({"name": x.name, "activity_points": x.activity_points})
        top_activity.append(dbuser)
    # Fetch top karma
    temp_list = sorted(guild.users, key=lambda x: x.karma, reverse=True)[:10]
    for x in temp_list:
        dbuser = services.AttrDict()
        dbuser.update({"name": x.name, "karma": x.karma})
        top_karma.append(dbuser)
    # Fetch top karma
    temp_list = sorted(guild.users, key=lambda x: x.tokens, reverse=True)[:10]
    for x in temp_list:
        dbuser = services.AttrDict()
        dbuser.update({"name": x.name, "tokens": x.tokens})
        top_tokens.append(dbuser)
    dbresults = services.AttrDict()
    dbresults.update({"top_messages": top_messages, "top_activity": top_activity,
                      "top_karma": top_karma, "top_tokens": top_tokens})
    session.commit()
    session.close()
    return dbresults
