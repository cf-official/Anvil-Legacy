from sqlalchemy import Column, String, Integer, DateTime
from database.dbbase import Base
from datetime import datetime


class KarmaEvents(Base):
    __tablename__ = 'karma_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_giving_id = Column(Integer)
    user_receiving_id = Column(Integer)
    channel_id = Column(String(20))
    datetime = Column(DateTime)

    def __init__(self, user_giving_id, user_receiving_id, channel_id):
        self.user_giving_id = user_giving_id
        self.user_receiving_id = user_receiving_id
        self.channel_id = channel_id
        self.datetime = datetime.today().date()
