from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Session = scoped_session(sessionmaker())
Base = declarative_base()


def initialize_sql(engine):
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
