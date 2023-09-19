import sys

sys.path.append("../..")

from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, get_user_exception, get_password_hash, verify_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str

class UserInfo(BaseModel):
    dob: str
    gender: str
    address: str
    phone: str
    userImage: str


@router.post("/userinfo")
async def add_userinfo(user_info: UserInfo,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    user_model = models.UserInfo()
    user_model.dob = user_info.dob
    user_model.userImage = user_info.userImage
    user_model.phone = user_info.phone
    user_model.address = user_info.address
    user_model.gender = user_info.gender
    users_id = db.query(models.Users.id).filter(models.Users.id == user.get("id"))
    user_model.users_id = users_id
    db.add(user_model)
    db.flush()
    db.commit()

@router.get("/")
async def get_user_info(user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    user_infoM = db.query(models.Users) \
        .filter(models.Users.id == user.get("id")) \
        .first()
    if user_infoM is not None:
        return user_infoM
    raise HTTPException(status_code=404, detail="User not found")





# @router.get("/user/")
# async def user(user_id: int,
#                        db: Session = Depends(get_db)):
#     user_model = db.query(models.Users) \
#         .filter(models.Users.id == user_id) \
#         .first()
#     if user_model is not None:
#         return user_model
#     return "Invalid User ID"


@router.put("/password")
async def user_password_change(user_verification: UserVerification, user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.Users) \
        .filter(models.Users.id == user.get('id')) \
        .first()

    if user_model is not None:
        if user_verification.username == user_model.username and verify_password(
                user_verification.password,
                user_model.hashed_password):
            user_model.hashed_password = get_password_hash(user_verification.new_password)
            db.add(user_model)
            db.commit()
            return 'Succesfull'
    return 'Invalid user or request'


@router.delete("/user")
async def delete_user(user_id: int,
                      db: Session = Depends(get_db)):
    user_model = db.query(models.Users) \
        .filter(models.Users.id == user_id) \
        .first()

    if user_model is None:
        return "Invalid user or request"

    db.query(models.Users).filter(models.Users.id == user_id).delete()

    db.commit()
    return 'User Deleted Successfully'
