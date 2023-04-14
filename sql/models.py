from sqlalchemy import URL, create_engine, Table
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


engine = create_engine("sqlite:///bot.db")
session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    tg_id = Column(Integer, primary_key=True)
    bird_name = Column(String)
    level_id = Column(Integer)
    level_progress = Column(Integer)
    task_completed = Column(Boolean)
    task_id = Column(Integer)

    def add_user(self, id):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, tg_id=id)
        if user is not None:
            return
        user = User(tg_id=id, level_id=0, level_progress=0, task_id=None, task_completed=None, bird_name="ПТИЦА")
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
        elif user.level_progress < 0:
            user.level_id -= 1
            user.level_progress = 100 + user.level_progress
        session.commit()

    def get_profile_data(self, id):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        return user


    def find_user(self, string):
        pass


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer)
    recipient_id = Column(Integer)
    text = Column(Text)
    rating = Column(Integer)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    def add_comment(self, sender_id, recipient_id):
        comment = Comment(sender_id=sender_id, recipient_id=recipient_id, text=None, rating=None)
        session.add(comment)
        session.commit()

    def edit_text(self, id, text):
        comment = session.get(Comment, id=id)
        comment.text = text
        session.commit()

    def rate_comment(self, id, rating):
        comment = session.get(Comment, id)
        comment.rating = rating
        session.commit()

class Levels(Base):
    __tablename__ = "birds"
    id = Column(Integer)
    bird_feature = Column(Text)
    bird_description = Column(Text)
    bird_task = Column(Text)
    bird_name = Column(Text)
    bird_level = Column(Integer)


Base.metadata.create_all(engine)

