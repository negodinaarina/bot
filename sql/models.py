from sqlalchemy import URL, create_engine, Table
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


engine = create_engine("sqlite:///bot.db")
session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    bird_name = Column(String)
    level_id = Column(Integer)
    level_progress = Column(Integer)
    task_completed = Column(Boolean)
    task_id = Column(Integer)

    def add_user(self, id):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        if user is not None:
            return
        user = User(id=id, level_id=0, level_progress=0, task_id=None, task_completed=None, bird_name="ПТИЦА")
        session.add(user)
        session.commit()


    def edit_bird_name(self, id, name):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        user.bird_name=name
        session.commit()

    def change_level_progress(self, id, points):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        user.level_progress = user.level_progress + points
        if user.level_progress > 100:
            user.level_id += 1
            user.level_progress = user.level_progress - 100
        session.commit()

    def get_profile_data(self, id):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        return user

Base.metadata.create_all(engine)

