from sqlalchemy import Column, String, Integer
from database.dbbase import Base


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(20))

    def __init__(self, channel_id):
        self.channel_id = channel_id
