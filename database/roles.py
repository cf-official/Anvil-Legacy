from sqlalchemy import Column, String, Integer
from database.dbbase import Base


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(String)
    point_requirement = Column(Integer)
    karma_requirement = Column(Integer)

    def __init__(self, role_id, point_requirement, karma_requirement):
        self.role_id = role_id
        self.point_requirement = point_requirement
        self.karma_requirement = karma_requirement
