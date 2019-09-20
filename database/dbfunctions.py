from database.dbbase import Session
from database.guilds import Guild
from database.users import User
from support.services import AttrDict
from datetime import date, datetime
from support import services

# Guild updates
def guild_add(guild):
    guild_add_users(guild)
    session = Session()
    guilds = session.query(Guild).all()
    # If new guild
    if sum(str(x.guild_id) == str(guild.id) for x in guilds) is 0:
        new_guild = Guild(guild.name, guild.id, date.today(), '.', True)
        session.add(new_guild)
    # If guild still attached
    elif sum(int(x.id) == 607163424362856458 for x in guild.members) is 1:
        guild = session.query(Guild).filter(Guild.guild_id == guild.id).first()
        guild.attached = True
    # If guild left while bot offline
    else:
        guild = session.query(Guild).filter(Guild.guild_id == guild.id).first()
        guild.attached = False
    session.commit()
    session.close()


def guild_remove(guild):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == guild.id).first()
    guild.attached = False
    session.commit()
    session.close()


# Add new users to DB, works both on build and on_guild_join
def guild_add_users(guild):
    # Prep session
    session = Session()
    users = guild.members
    guild = session.query(Guild).filter(Guild.guild_id == guild.id).first()
    # Create new users and add them to guild
    for user in users:
        if not user.bot:
            # Check if user already exists for guild
            if sum(str(x.user_id) == str(user.id) for x in guild.users) is 0:
                new_user = User(user.name, user.id, 0, 0, 0)
                guild.users.append(new_user)
                session.add(new_user)
    session.commit()
    session.close()


# Updates amount of messages stored in DB based on arg: increment
def update_user_messages(user, increment):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == user.guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(user.id)), None)
    user.messages_sent += increment
    session.commit()
    session.close()


# Updates amount of activity points stored in DB based on arg: increment
def update_user_activity(user, increment):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == user.guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(user.id)), None)
    user.activity_points += increment
    user.last_message = datetime.now()
    session.commit()
    session.close()


# Updates amount of karma stored in DB based on arg: increment
def update_user_karma(user, increment):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == user.guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(user.id)), None)
    user.karma += increment
    session.commit()
    session.close()


def retrieve_user(user):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == user.guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(user.id)), None)
    dbuser = AttrDict()
    dbuser.update({"name" : user.name, "user_id" : user.user_id, "messages_sent" : user.messages_sent,
                   "activity_points" : user.activity_points, "karma" : user.karma, "last_message" : user.last_message})
    session.commit()
    session.close()
    return dbuser


def check_user_last_message(user):
    session = Session()
    guild = session.query(Guild).filter(Guild.guild_id == user.guild.id).first()
    user = next((x for x in guild.users if int(x.user_id) == int(user.id)), None)
    if user.last_message is None:
        user.last_message = datetime.now()
    if services.difference_in_minutes(user.last_message, datetime.now()) > 1:
        result = True
    else:
        result = False
    user.last_message = datetime.now()
    session.commit()
    session.close()
    return result
