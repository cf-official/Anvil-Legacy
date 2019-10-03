from sqlalchemy import Column, String, Integer, DateTime
from database.dbbase import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    user_id = Column(String)
    messages_sent = Column(Integer)
    activity_points = Column(Integer)
    karma = Column(Integer)
    last_message = Column(DateTime)

    def __init__(self, name, user_id, messages_sent, acivity_points, karma, last_message):
        self.name = name
        self.user_id = user_id
        self.messages_sent = messages_sent
        self.activity_points = acivity_points
        self.karma = karma
        self.last_message = last_message
