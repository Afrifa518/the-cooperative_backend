import sys

sys.path.append("../..")

from fastapi import Depends, HTTPException, status, APIRouter, Form
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from sqlalchemy import desc
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "JGUGVjhbhFY5R655DF65r7RFTYCj6Tytfgchfut6"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users) \
        .filter(models.Users.username == username) \
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=7)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except JWTError:
        raise get_user_exception()


@router.get("/refresh")
async def refresh_access_token(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    username = current_user["username"]
    token_expires = timedelta(hours=7)
    new_token = create_access_token(username, user_id, expires_delta=token_expires)

    return {"token": new_token}


@router.get("/all/roles")
async def get_all_roles(user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.UserRoles).all()


@router.post("/create/user")
async def create_new_user(username: str = Form(...),
                          firstName: str = Form(...),
                          middleName: Optional[str] = Form(None),
                          lastName: str = Form(...),
                          email: str = Form(...),
                          hashed_password: str = Form(...),
                          dob: str = Form(...),
                          gender: str = Form(...),
                          address: Optional[str] = Form(None),
                          phone: Optional[str] = Form(None),
                          role_id: int = Form(...),
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    create_user_model = models.Users()
    create_user_model.username = username
    create_user_model.firstName = firstName
    create_user_model.middleName = middleName
    create_user_model.lastName = lastName
    create_user_model.email = email
    create_user_model.role_id = role_id
    create_user_model.date_joined = datetime.now()
    hash_password = get_password_hash(hashed_password)
    create_user_model.hashed_password = hash_password

    db.add(create_user_model)
    db.commit()

    new_person = db.query(models.Users).order_by(desc(models.Users.id)).first()

    add_details = models.UserInfo(
        dob=dob,
        gender=gender,
        address=address,
        phone=phone,
        userImage=None,
        users_id=new_person.id,
    )
    db.add(add_details)
    db.commit()

    return "New User Added"


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return {"error": "Invalid Credentials"}

    token_expires = timedelta(hours=7)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)
    role = db.query(models.UserRoles).join(models.Users, models.Users.role_id == models.UserRoles.id).filter(
        models.Users.id == user.id).first()

    return {"token": token, "role": role.id}


def token_exception():
    token_exception_responce = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return token_exception_responce


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception
