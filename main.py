from fastapi import FastAPI
import models
import logging
from database import engine
import transactions
import permissions
import members
import commodities
import auth
import associations
import accounts
import users
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# , "http://localhost:3000""ORIGIN",
app = FastAPI()
# handler = Mangum(app)
# origin = os.getenv("https://the-cooperative-frontend.vercel.app")
# Configure FastAPI logger with custom formatter including timestamp
# formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# handler = logging.StreamHandler()
# handler.setFormatter(formatter)

# Set logger level to DEBUG
logging.basicConfig(level=logging.DEBUG)
# fastapi_logger.handlers = [handler]

app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    # allow_origins=[""])
    allow_origins=["https://the-cooperative-frontend.vercel.app"])

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(associations.router)
app.include_router(members.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(commodities.router)
app.include_router(permissions.router)


@app.get("/debug")
def debug_endpoint():
    logging.debug("This is a debug message.")
    return {"message": "Debug message sent to logs"}


handler = Mangum(app)
