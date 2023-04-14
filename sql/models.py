from sqlalchemy import URL, create_engine, Table
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


engine = create_engine("sqlite:///bot.db")
session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    tg_id = Column(String, primary_key=True)
    tg_nickname = Column(String)
    bird_name = Column(String)
    level = Column(Integer)
    level_progress = Column(Integer)
    task_completed = Column(Boolean)
    task_id = Column(Integer)


    def add_user(self, id, nickname):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = User(tg_id=id, tg_nickname=nickname, level=1, level_progress=0, task_id=None, task_completed=None,
                        bird_name="ПТИЦА")
        session.add(user)
        session.commit()


    def if_exists(self, id):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        if user is None:
            return False
        else:
            return True

    def edit_bird_name(self, id, name):
        user = session.get(User, id)
        user.bird_name=name
        session.commit()

    @staticmethod
    def change_level_progress(id, points):
        user = session.get(User, id)
        user.level_progress = user.level_progress + points
        if user.level_progress > 100:
            user.level += 1
            user.level_progress = user.level_progress - 100
        elif user.level_progress < 0:
            user.level -= 1
            user.level_progress = 100 + user.level_progress
        session.commit()

    def get_profile_data(self, id):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        return user


    def find_user(self, string):
        try:
            user = session.get(User, tg_nickname=string)
            return user
        except:
            return "Неверно введен ник, попробуйте снова"

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


    @staticmethod
    def add_comment(sender_id, recipient_id):
        comment = Comment(sender_id=sender_id, recipient_id=recipient_id, text=None, rating=None)
        session.add(comment)
        session.commit()

    @staticmethod
    def edit_text(id, text):
        comment = session.get(Comment, id=id)
        comment.text = text
        session.commit()

    @staticmethod
    def rate_comment(id, rating):
        comment = session.get(Comment, id)
        comment.rating = rating
        session.commit()

class Levels(Base):
    __tablename__ = "birds"
    id = Column(Integer, primary_key=True)
    bird_feature = Column(Text)
    bird_description = Column(Text)
    bird_task = Column(Text)
    bird_name = Column(Text)
    bird_level = Column(Integer)

    def get_bird_data(self, level):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        bird_info = session.get(Levels, level)
        return bird_info


Base.metadata.create_all(engine)

