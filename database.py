from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgres://cooperative_database_user:jTQNnH8XtJNTOmegy09q6e2W6sHUF8Zv@dpg-ckm3nfo710pc73falujg-a.oregon-postgres.render.com/cooperative_database"
    # "/postgresql://postgres:password@localhost/FinanceDept"
# os.environ
# postgresql://cooperative_database_user:jTQNnH8XtJNTOmegy09q6e2W6sHUF8Zv@dpg-ckm3nfo710pc73falujg-a.oregon-postgres.render.com/cooperative_database
# client = MongoClient("mongodb+srv://Afrifa518:Kindomlife518@cluster0.nepgwqm.mongodb.net/?retryWrites=true&w=majority")
#
# db = client.todo_db
# collection_name = db["todo_collection"]


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
