import base64
import sys

sys.path.append("..")

from fastapi import Depends, APIRouter, File, UploadFile, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user, get_user_exception

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
                       marital_status: Optional[str] = Form(None),
                       sinn_number: Optional[str] = Form(None),
                       basic_salary: Optional[float] = Form(None),
                       account_name: Optional[str] = Form(None),
                       account_number: Optional[int] = Form(None),
                       bank_name: Optional[str] = Form(None),
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
    user_model.marital_status = marital_status
    user_model.sinn_number = sinn_number
    user_model.basic_salary = basic_salary
    user_model.account_name = account_name
    user_model.account_number = account_number
    user_model.bank_name = bank_name
    users_id = user.get("id")
    user_model.users_id = users_id
    db.add(user_model)
    db.flush()
    db.commit()

    return "Successfully Updated"


@router.post("/new/role")
async def create_new_role(role_name: str = Form(...),
                          db: Session = Depends(get_db)):
    new = models.UserRoles(
        role_name=role_name,
        create_member=0,
        update_member=0,
        delete_member=0,
        view_member=0,
        create_association=0,
        update_association=0,
        view_association=0,
        delete_association=0,
        create_society=0,
        update_society=0,
        view_society=0,
        delete_society=0,
        create_association_type=0,
        update_association_type=0,
        view_association_type=0,
        delete_association_type=0,
        create_savings_transactions=0,
        update_savings_transactions=0,
        view_savings_transactions=0,
        delete_savings_transactions=0,
        request_loan_transactions=0,
        update_loan_request=0,
        view_loan_transactions=0,
        delete_loan_transactions=0,
        download_loan_advise=0,
        approve_loan_requests=0,
        disburse_approved_loans=0,
        create_shares_transactions=0,
        view_share_transactions=0,
        download_share_cert=0,
        delete_share_transactions=0,
        view_association_passbook=0,
        view_association_momo_account=0,
        set_association_momo_bal=0,
        view_society_account=0,
        view_society_reconciliatio_form=0,
        reconcile_balances=0,
        view_bank_accounts=0,
        create_bank_accounts=0,
        create_bank_transactions=0,
        view_bank_transactions=0,
        update_bank_transactions=0,
        delete_bank_transactions=0,
        create_savings_account=0,
        update_savings_account=0,
        delete_savings_account=0,
        create_loan_account=0,
        update_loan_account=0,
        delete_loan_account=0,
        create_share_account=0,
        update_share_account=0,
        delete_share_account=0,
        create_warehouse=0,
        create_commodity=0,
        view_savings_account=0,
        view_loans_account=0,
        view_shares_account=0,
        view_commodity_account=0,
        view_warehouse=0,
        view_expense=0,
        expense_approve=0,
        expense_disbures=0,
        view_rejected=0,
    )
    db.add(new)
    db.commit()

    return "New Role Created"


@router.get("/user/society")
async def get_user_soc(user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    soc = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    return {"Soc": soc.society_id}


@router.delete("/delete/{role_id}")
async def delete_role(role_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    db.query(models.UserRoles).filter(models.UserRoles.id == role_id).delete()
    db.commit()

    return "Role Deleted"


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


@router.get("/su")
async def get_user_info(user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    user_info = db.query(models.Users.username,
                         models.Users.email,
                         models.Users.middleName,
                         models.Users.firstName,
                         models.Users.lastName,
                         models.UserRoles.role_name) \
        .select_from(models.Users) \
        .join(models.UserRoles, models.UserRoles.id == models.Users.role_id) \
        .filter(models.Users.id == user.get("id")) \
        .first()

    user_infoM = db.query(models.Users.username,
                          models.Users.email,
                          models.Users.middleName,
                          models.Users.firstName,
                          models.Users.lastName) \
        .filter(models.Users.id == user.get("id")) \
        .first()

    if user_info:
        response = {
            "username": user_info.username,
            "email": user_info.email,
            "middleName": user_info.middleName,
            "firstName": user_info.firstName,
            "lastName": user_info.lastName,
            "role_name": user_info.role_name
        }
    else:
        response = {
            "username": user_infoM.username,
            "email": user_infoM.email,
            "middleName": user_infoM.middleName,
            "firstName": user_infoM.firstName,
            "lastName": user_infoM.lastName,
            "role_name": 'N/A'
        }

    return response


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


@router.get("/details/one/{user_id}")
async def get_one_user_details(user_id: int,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    details = db.query(models.UserInfo) \
        .filter(models.UserInfo.users_id == user_id) \
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
                       models.UserInfo.gender,
                       models.UserInfo.account_name,
                       models.UserInfo.account_number,
                       models.UserInfo.bank_name,
                       models.UserInfo.basic_salary,
                       models.UserInfo.marital_status,
                       models.UserInfo.sinn_number) \
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
                          models.Users.middleName,
                          models.Users.email,
                          models.Users.id,
                          models.Users.date_joined,
                          models.UserInfo.userImage,
                          models.UserInfo.gender,
                          models.UserInfo.phone,
                          models.UserInfo.address,
                          models.Users.hashed_password,
                          models.UserInfo.dob,
                          models.UserInfo.marital_status,
                          models.UserInfo.sinn_number,
                          models.UserInfo.account_name,
                          models.UserInfo.account_number,
                          models.UserInfo.bank_name,
                          models.UserInfo.basic_salary,
                          models.UserRoles.role_name,
                          models.Society.society) \
        .select_from(models.Users) \
        .join(models.UserInfo, models.UserInfo.users_id == models.Users.id) \
        .join(models.Society, models.Society.id == models.Users.society_id) \
        .outerjoin(models.UserRoles, models.Users.role_id == models.UserRoles.id) \
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
            "role": user_one.role_name,
            "password": user_one.hashed_password,
            "userImage": image,
            "gender": user_one.gender,
            "phone": user_one.phone,
            "address": user_one.address,
            "dob": user_one.dob,
            "date_joined": user_one.date_joined,
            "marital_status": user_one.marital_status,
            "sinn_number": user_one.sinn_number,
            "account_name": user_one.account_name,
            "account_number": user_one.account_number,
            "bank_name": user_one.bank_name,
            "basic_salary": user_one.basic_salary,
            "society": user_one.society,
        })

    return data


class UserUpdate(BaseModel):
    user_idd: int
    role_id: Optional[int]
    basic_salary: Optional[float]


@router.patch("/updates/user")
async def update_user_role(updates: UserUpdate,
                           user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    if updates.role_id:
        person = db.query(models.Users).filter(models.Users.id == updates.user_idd) \
            .update({models.Users.role_id: updates.role_id})
        db.commit()
    if updates.basic_salary:
        person_salary = db.query(models.UserInfo).filter(models.UserInfo.users_id == updates.user_idd) \
            .update({models.UserInfo.basic_salary: updates.basic_salary})
        db.commit()

    person = db.query(models.Users).filter(models.Users.id == updates.user_idd) \
        .first()
    person_salary = db.query(models.UserInfo).filter(models.UserInfo.users_id == updates.user_idd) \
        .first()


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
        user_model.hashed_password = user_verification.new_password
        db.commit()
        return 'Password Changed Successfully'


@router.delete("/user/delete/{user_id}")
async def delete_user(user_id: int,
                      db: Session = Depends(get_db)):
    user_model = db.query(models.Users) \
        .filter(models.Users.id == user_id) \
        .first()

    if user_model is None:
        return "Invalid user or request"

    db.query(models.UserAccount).filter(models.UserAccount.user_id == user_id).delete()
    db.commit()
    db.query(models.UserInfo).filter(models.UserInfo.users_id == user_id).delete()
    db.commit()
    db.query(models.Users).filter(models.Users.id == user_id).delete()
    db.commit()

    return 'User Deleted Successfully'
