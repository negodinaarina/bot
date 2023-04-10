import sqlalchemy
from sqlalchemy import URL, create_engine
url_object = URL.create(
    "postgresql+pg8000",
    username="dbbot",
    password="1111",  # plain (unescaped) text
    host="pghost10",
    database="appdb",
)

engine = create_engine(url_object)
