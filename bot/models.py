import sqlalchemy
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

url_object = URL.create(
    "postgresql+pg8000",
    username="postgres",
    password="1111",  # plain (unescaped) text
    host="pghost10",
    database="botdb",
)

engine = create_engine(url_object)
session = Session(engine)


# class Base(DeclarativeBase):
#     pass
#
#
# class User(Base):
#     __tablename__ = "users"
#     id: Mapped[int] = mapped_column(primary_key=True)
#
