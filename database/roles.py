from sqlalchemy import Column, String, Integer
from database.dbbase import Base


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(String(20))
    message_requirement = Column(Integer)
    point_requirement = Column(Integer)
    karma_requirement = Column(Integer)
    token_requirement = Column(Integer)

    def __init__(self, role_id, message_requirement, point_requirement, karma_requirement, token_requirement):
        self.role_id = role_id
        self.message_requirement = message_requirement
        self.point_requirement = point_requirement
        self.karma_requirement = karma_requirement
        self.token_requirement = token_requirement
