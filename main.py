from fastapi import FastAPI
import models
from database import engine
from routers import auth, users, associations, members, accounts, transactions, commodities
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_origins=["http://localhost:3000"])

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(associations.router)
app.include_router(members.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(commodities.router)
