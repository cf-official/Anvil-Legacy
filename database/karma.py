from sqlalchemy import Column, Integer, DateTime
from database.dbbase import Base


class KarmaEvents(Base):
    __tablename__ = 'karma_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_giving_id = Column(Integer)
    user_receiving_id = Column(Integer)
    datetime = Column(DateTime)

    def __init__(self, user_giving_id, user_receiving_id, datetime, ):
        self.user_giving_id = user_giving_id
        self.user_receiving_id = user_receiving_id
        self.datetime = datetime
