from sqlalchemy import URL, create_engine, Table
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime


engine = create_engine("sqlite:///bot.db")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    tg_id = Column(String, primary_key=True)
    tg_nickname = Column(String)
    bird_name = Column(String)
    level = Column(Integer)
    level_progress = Column(Integer)
    last_mail = Column(DateTime)
    last_fact = Column(Integer)
    admin = Column(Boolean)


    def add_user(self, id, nickname):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        user = User(tg_id=id, tg_nickname=nickname, level=1, level_progress=0,
                        bird_name="ПТИЦА", admin=False, last_mail=yesterday, last_fact=0)
        session.add(user)
        session.commit()


    def is_admin(self, id):
        user = session.get(User, id)
        return user.admin

    def change_status(self, id, status):
        user = session.get(User, id)
        user.admin = status
        session.commit()

    def if_exists(self, id):
        user = session.get(User, id)
        if user is None:
            return False
        else:
            return True

    def edit_bird_name(self, id, name):
        user = session.get(User, id)
        user.bird_name = name
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
        user = session.get(User, id)
        return user


    def find_user(self, string):
        return


    def all_users(self):
        users = session.query(User).all()
        return users

    def change_mail_date(self, id, date):
        user = session.get(User, id)
        user.last_mail = date
        session.commit()


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer)
    recipient_id = Column(Integer)
    text = Column(Text)
    rating = Column(Integer)


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
    id = Column(Integer, autoincrement=True, primary_key=True)
    bird_name = Column(Text, unique=True)
    bird_feature = Column(Text)
    bird_description = Column(Text)
    bird_task = Column(Text)
    bird_level = Column(Integer)


    def get_bird_data(self, level):
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
        event = Event(title=title, description=description, date=date, time=time, place=place, price=price, code_phrase=phrase)
        session.add(event)
        session.commit()

    def get_event(self, phrase):
        event_info = session.query(Event).filter_by(code_phrase=phrase).first()
        return event_info


class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(String, primary_key=True)
    chat_name = Column(String)

    @staticmethod
    def get_all_chats():
        chats = session.query(Chat).all()
        return chats

    def add_chat(self, id, title):
        chat = Chat(chat_id=id, chat_name=title)
        session.add(chat)
        session.commit()


    def get_chat_by_title(self, title):
        chat = session.query(Chat).filter_by(chat_name=title).first()
        return chat

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    event_id = Column(Integer)

    def get_attendance(self, user_id, event_id):
        attend = session.query(Attendance).filter_by(user_id=user_id, event_id=event_id).first()
        if attend is None:
            return False
        else:
            return True

    def add_attendance(self, user_id, event_id):
        attend = Attendance(user_id=user_id, event_id=event_id)
        session.add(attend)
        session.commit()


class Facts(Base):
    __tablename__="facts"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    user_name = Column(String)
    fact = Column(Text)
    is_true = Column(Boolean)

    def add_fact(self, user_id, user_name, fact, is_true):
        fact = Facts(user_id=user_id, user_name=user_name, fact=fact, is_true=is_true)
        session.add(fact)
        session.commit()


    def get_fact(self, id, fact_num):
        fact = session.query(Facts).filter(Facts.user_id != id, Facts.id > fact_num).first()
        return fact


Base.metadata.create_all(engine)

if not session.query(Levels).first():

    chayka = Levels(
        bird_name='Чайка',
        bird_feature='Индивидуалистка',
        bird_description='Любит рыбачить',
        bird_task='Рыбачить и орать',
        bird_level=1
    )

    golub = Levels(
        bird_name='Голубь',
        bird_feature='Влюбленный',
        bird_description='Со всеми воркует',
        bird_task='Со всеми ворковать',
        bird_level=2
    )

    vorob = Levels(
        bird_name='Воробей',
        bird_feature='Боец',
        bird_description='Маленький да удаленький',
        bird_task='Пищать и драться',
        bird_level=3
    )

    session.add(chayka)
    session.add(golub)
    session.add(vorob)
    session.commit()
