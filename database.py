from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")

# postgresql://cooperative_database_user:jTQNnH8XtJNTOmegy09q6e2W6sHUF8Zv@dpg-ckm3nfo710pc73falujg-a.oregon-postgres.render.com/cooperative_database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
