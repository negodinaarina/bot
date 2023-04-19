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
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        user = session.get(User, id)
        user.bird_name = name
        session.commit()

    @staticmethod
    def change_level_progress(id, points):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
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
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        return


    def all_users(self):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        users = session.query(User).all()
        return users


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer)
    recipient_id = Column(Integer)
    text = Column(Text)
    rating = Column(Integer)


    @staticmethod
    def add_comment(sender_id, recipient_id):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        comment = Comment(sender_id=sender_id, recipient_id=recipient_id, text=None, rating=None)
        session.add(comment)
        session.commit()

    @staticmethod
    def edit_text(id, text):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        comment = session.get(Comment, id=id)
        comment.text = text
        session.commit()

    @staticmethod
    def rate_comment(id, rating):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
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

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    date = Column(String)
    time = Column(String)
    place = Column(String)
    price = Column(Integer)
    code_phrase = Column(String)

    def create_event(self, title, description, date, time, place, price, phrase):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        event = Event(title=title, description=description, date=date, time=time, place=place, price=price, code_phrase=phrase)
        session.add(event)
        session.commit()

    def get_event(self, phrase):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        event_info = session.query(Event).filter_by(code_phrase=phrase).first()
        return event_info


class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(String, primary_key=True)
    chat_name = Column(String)

    @staticmethod
    def get_all_chats():
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        chats = session.query(Chat).all()
        return chats

    def add_chat(self, id, title):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        chat = Chat(chat_id=id, chat_name=title)
        session.add(chat)
        session.commit()


    def get_chat_by_title(self, title):
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        chat = session.query(Chat).filter_by(chat_name=title).first()
        return chat



Base.metadata.create_all(engine)

