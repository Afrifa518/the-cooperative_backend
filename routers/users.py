import base64
import sys

sys.path.append("../..")

from fastapi import Depends, HTTPException, APIRouter, File, UploadFile, Form
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


@router.post("/userinfo")
async def add_userinfo(dob: str = Form(...),
                       gender: str = Form(...),
                       address: str = Form(...),
                       phone: str = Form(...),
                       firstName: str = Form(...),
                       middleName: str = Form(...),
                       lastName: str = Form(...),
                       email: str = Form(...),
                       username: str = Form(...),
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()


    update_data = {
        models.Users.username: username,
        models.Users.firstName: firstName,
        models.Users.middleName: middleName,
        models.Users.lastName: lastName,
        models.Users.email: email,
    }

    user_ankasa = db.query(models.Users) \
        .filter(models.Users.id == user.get("id")) \
        .update(update_data)

    db.commit()

    user_model = db.query(models.UserInfo).filter(models.UserInfo.users_id == user.get("id")).first()
    user_model.dob = dob
    user_model.phone = phone
    user_model.address = address
    user_model.gender = gender
    users_id = user.get("id")
    user_model.users_id = users_id
    db.add(user_model)
    db.flush()
    db.commit()

    return "Successfully Updated"


# userImage: UploadFile | None = None,

@router.post("/picture/update")
async def update_picture(userImage: UploadFile = File(...),
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    if userImage:
        userImagee = userImage.file.read()
    else:
        p = db.query(models.UserInfo).filter(models.UserInfo.users_id == user.get("id")).first()
        userImagee = p.userImage
    update_data = {
        models.UserInfo.userImage: userImagee,
    }
    user_ankasa = db.query(models.UserInfo) \
        .filter(models.UserInfo.users_id == user.get("id")) \
        .update(update_data)
    db.commit()

    return "Successfully Updated"


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


@router.get("/details")
async def get_user_details(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    details = db.query(models.UserInfo) \
        .filter(models.UserInfo.users_id == user.get("id")) \
        .first()
    pic = details.userImage if details.userImage else None
    image = base64.b64encode(pic).decode("utf-8") if pic else None
    return image


@router.get("/details/all")
async def get_user_details(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    details = db.query(models.UserInfo.dob,
                       models.UserInfo.phone,
                       models.UserInfo.address,
                       models.UserInfo.gender) \
        .filter(models.UserInfo.users_id == user.get("id")) \
        .first()

    return details


@router.get("/user/all")
async def get_all_users(user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.Users.username,
                          models.Users.firstName,
                          models.Users.lastName,
                          models.Users.email,
                          models.Users.id,
                          models.Users.role,
                          models.UserInfo.userImage,
                          models.UserInfo.gender,
                          models.UserInfo.phone,
                          models.UserInfo.address,
                          models.UserInfo.dob) \
        .select_from(models.Users) \
        .join(models.UserInfo, models.UserInfo.users_id == models.Users.id) \
        .filter(models.Users.id != user.get("id")) \
        .all()

    data = []

    for user_one in user_model:
        pic = user_one.userImage if user_one.userImage else None
        image = base64.b64encode(pic).decode("utf-8") if pic else None
        data.append({
            "username": user_one.username,
            "firstName": user_one.firstName,
            "lastName": user_one.lastName,
            "email": user_one.email,
            "id": user_one.id,
            "role": user_one.role,
            "userImage": image,
            "gender": user_one.gender,
            "phone": user_one.phone,
            "address": user_one.address,
            "dob": user_one.dob
        })

    return data




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
