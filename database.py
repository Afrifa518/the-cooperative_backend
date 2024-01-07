import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = ("postgresql://postgres:Kindomlife518@localhost/FinanceDept")

# MAIL_USERNAME=os.getenv("MAIL_USERNAME")
# MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
# MAIL_FROM=os.getenv("MAIL_FROM")
# MAIL_PORT=os.getenv("MAIL_PORT")
# MAIL_SERVER=os.getenv("MAIL_SERVER")
# MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME")
# service_id = service_c9e4iwy
#"DATABASE_URL","postgresql://afrifa518:Kindomlife518@my-db-instance.cx8m0iesmzvp.eu-west-2.rds.amazonaws.com/theCooperativeDb"
SQLALCHEMY_DATABASE_URL = "postgresql://afrifa518:Kindomlife518@my-db-instance.cx8m0iesmzvp.eu-west-2.rds.amazonaws.com/theCooperativeDb"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
