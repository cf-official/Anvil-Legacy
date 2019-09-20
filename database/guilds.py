from sqlalchemy import Column, String, Integer, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from database.dbbase import Base
from database import users


guilds_users_association = Table(
    'guilds_users', Base.metadata,
    Column('guild_id', Integer, ForeignKey('guilds.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    guild_id = Column(String)
    join_date = Column(Date)
    prefix = Column(String)
    attached = Column(Integer)

    users = relationship("User", secondary='guilds_users', cascade="save-update")

    def __init__(self, name, guild_id, join_date, prefix, attached):
        self.name = name
        self.guild_id = guild_id
        self.join_date = join_date
        self.prefix = prefix
        self.attached = attached


