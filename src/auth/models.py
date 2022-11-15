from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from ..database import engine

Base = declarative_base()


# TODO Replace type of email
class User(Base):
    __tablename__: str = 'users'

    id: int = Column(Integer, primary_key=True)
    email: str = Column(String, unique=True)
    username: str = Column(String, unique=True)
    hashed_password: str = Column(String)


Base.metadata.create_all(engine)
