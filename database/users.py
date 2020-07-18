from sqlalchemy import Column, String, Integer, DateTime
from database.dbbase import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))
    user_id = Column(String(20))
    messages_sent = Column(Integer)
    activity_points = Column(Integer)
    tokens = Column(Integer)
    karma = Column(Integer)
    last_message = Column(DateTime)

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id
        self.messages_sent = 0
        self.activity_points = 0
        self.tokens = 0
        self.karma = 0
        self.last_message = datetime.now()
