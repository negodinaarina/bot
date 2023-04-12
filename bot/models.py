from sqlalchemy import URL, create_engine, Table
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


engine = create_engine("sqlite:///bot.db")
session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    bird_name = Column(String)
    speed_level = Column(Integer)
    level_progress = Column(Integer)


Base.metadata.create_all(engine)

