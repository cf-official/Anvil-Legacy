from sqlalchemy import Column, String, Integer, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from database.dbbase import Base
from datetime import date
# This imports are important because it changes loading order.
from database import users
from database import roles
from database import channels


guilds_users_association = Table(
    'guilds_users', Base.metadata,
    Column('guild_id', Integer, ForeignKey('guilds.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

guilds_roles_association = Table(
    'guilds_roles', Base.metadata,
    Column('guild_id', Integer, ForeignKey('guilds.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

guilds_channels_association = Table(
    'guilds_channels', Base.metadata,
    Column('guild_id', Integer, ForeignKey('guilds.id')),
    Column('channel_id', Integer, ForeignKey('channels.id'))
)


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    guild_id = Column(String(20))
    join_date = Column(Date)
    prefix = Column(String(32))
    attached = Column(Integer)
    karma_emoji = Column(String(32))
    log_channel_id = Column(String(20))

    users = relationship("User", secondary='guilds_users', cascade="save-update")
    roles = relationship("Role", secondary='guilds_roles', cascade="save-update")
    channels = relationship("Channel", secondary='guilds_channels', cascade="save-update")

    def __init__(self, name, guild_id):
        self.name = name
        self.guild_id = guild_id
        self.join_date = date.today()
        self.prefix = '.'
        self.attached = True
        self.karma_emoji = None
        self.log_channel_id = None
