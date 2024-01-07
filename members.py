import sys

sys.path.append("..")

from typing import Optional, Union
from fastapi import Depends, HTTPException, APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import desc
from auth import get_current_user, get_user_exception
import base64
from datetime import datetime

router = APIRouter(
    prefix="/members",
    tags=["members"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class AssociationMembers(BaseModel):
    member_id: int
    association_id: int


# @router.post("/create")
# async def create_member(firstName: str = Form(...),
#                         middleName: Optional[str] = Form(None),
#                         lastName: str = Form(...),
#                         dob: str = Form(...),
#                         gender: str = Form(...),
#                         phone: str = Form(...),
#                         otherPhone: str = Form(None),
#                         address: str = Form(...),
#                         otherAddress: str = Form(None),
#                         ghCardNumber: str = Form(...),
#                         nextOfKin: str = Form(...),
#                         ghCardImage: UploadFile = File(...),
#                         memberImage: UploadFile = File(...),
#                         otherName: str = Form(...),
#                         commonname: str = Form(...),
#                         MaritalStatus: str = Form(...),
#                         EducationLevel: str = Form(...),
#                         Town: str = Form(...),
#                         ruralOrUrban: str = Form(...),
#                         user: dict = Depends(get_current_user),
#                         db: Session = Depends(get_db)
#                         ):
#     if user is None:
#         raise get_user_exception()
#
#     gh_card_image_data = ghCardImage.file.read()
#     member_image_data = memberImage.file.read()
#
#     member_model = models.Members(
#         firstname=firstName,
#         middlename=middleName,
#         lastname=lastName,
#         dob=dob,
#         gender=gender,
#         phone=phone,
#         otherPhone=otherPhone,
#         address=address,
#         otherAddress=otherAddress,
#         ghCardNumber=ghCardNumber,
#         nextOfKin=nextOfKin,
#         ghCardImage=gh_card_image_data,
#         memberImage=member_image_data,
#         otherName=otherName,
#         commonname=commonname,
#         MaritalStatus=MaritalStatus,
#         EducationLevel=EducationLevel,
#         Town=Town,
#         ruralOrUrban=ruralOrUrban,
#     )
#
#     db.add(member_model)
#     db.commit()
#
#     return "Created Successfully"


@router.post("/register/individual")
async def register_single_member(firstname: str = Form(...),
                                 middlename: Optional[str] = Form(None),
                                 lastname: Optional[str] = Form(None),
                                 dob: Optional[str] = Form(None),
                                 gender: str = Form(...),
                                 phone: Optional[str] = Form(None),
                                 otherPhone: Optional[str] = Form(None),
                                 address: Optional[str] = Form(None),
                                 otherAddress: Optional[str] = Form(None),
                                 ghCardNumber: Optional[str] = Form(None),
                                 nextOfKin: Optional[str] = Form(None),
                                 ghCardImage: Union[UploadFile, str, None] = None,
                                 memberImage: Union[UploadFile, str, None] = None,
                                 otherName: Optional[str] = Form(None),
                                 commonname: Optional[str] = Form(None),
                                 MaritalStatus: Optional[str] = Form(None),
                                 EducationLevel: Optional[str] = Form(None),
                                 Town: Optional[str] = Form(None),
                                 ruralOrUrban: Optional[str] = Form(None),
                                 db: Session = Depends(get_db),
                                 user: dict = Depends(get_current_user)
                                 ):
    if user is None:
        raise get_user_exception()
    if ghCardNumber:
        if db.query(models.Members).filter_by(ghcardnumber=ghCardNumber).first():
            raise HTTPException(status_code=400, detail="Card Number already exists")
    else:
        pass

    if isinstance(ghCardImage, str):
        gh_card_image_data = None

    else:
        gh_card_image_data = ghCardImage.file.read() if ghCardImage else None
    if isinstance(memberImage, str):
        member_image_data = None
    else:
        member_image_data = memberImage.file.read() if memberImage else None

    member_model = models.Members(
        firstname=firstname,
        middlename=middlename,
        lastname=lastname,
        dob=dob,
        gender=gender,
        phone=phone,
        otherPhone=otherPhone,
        address=address,
        otherAddress=otherAddress,
        ghcardnumber=ghCardNumber,
        nextOfKin=nextOfKin,
        ghCardImage=gh_card_image_data,
        memberImage=member_image_data,
        otherName=otherName,
        commonname=commonname,
        MaritalStatus=MaritalStatus,
        EducationLevel=EducationLevel,
        Town=Town,
        ruralOrUrban=ruralOrUrban,
    )

    db.add(member_model)
    db.commit()

    member_id = db.query(models.Members) \
        .order_by(desc(models.Members.member_id)) \
        .first()
    default_registration_account_individuals(member_Id=member_id.member_id, db=db)

    return "Member Registered Successfully"


@router.post("/register")
async def create_member_and_register_association(association_id: int = Form(...),
                                                 firstname: str = Form(...),
                                                 middlename: Optional[str] = Form(None),
                                                 lastname: Optional[str] = Form(None),
                                                 dob: Optional[str] = Form(None),
                                                 gender: str = Form(...),
                                                 phone: Optional[str] = Form(None),
                                                 otherPhone: Optional[str] = Form(None),
                                                 address: Optional[str] = Form(None),
                                                 otherAddress: Optional[str] = Form(None),
                                                 ghCardNumber: Optional[str] = Form(None),
                                                 nextOfKin: Optional[str] = Form(None),
                                                 ghCardImage: Union[UploadFile, str, None] = None,
                                                 memberImage: Union[UploadFile, str, None] = None,
                                                 otherName: Optional[str] = Form(None),
                                                 commonname: Optional[str] = Form(None),
                                                 MaritalStatus: Optional[str] = Form(None),
                                                 EducationLevel: Optional[str] = Form(None),
                                                 Town: Optional[str] = Form(None),
                                                 ruralOrUrban: Optional[str] = Form(None),
                                                 db: Session = Depends(get_db),
                                                 user: dict = Depends(get_current_user)
                                                 ):
    if user is None:
        raise get_user_exception()
    if ghCardNumber:
        if db.query(models.Members).filter_by(ghcardnumber=ghCardNumber).first():
            raise HTTPException(status_code=400, detail="Card Number already exists")
    else:
        pass

    if isinstance(ghCardImage, str):
        gh_card_image_data = None

    else:
        gh_card_image_data = ghCardImage.file.read() if ghCardImage else None
    if isinstance(memberImage, str):
        member_image_data = None
    else:
        member_image_data = memberImage.file.read() if memberImage else None

    member_model = models.Members(
        firstname=firstname,
        middlename=middlename,
        lastname=lastname,
        dob=dob,
        gender=gender,
        phone=phone,
        otherPhone=otherPhone,
        address=address,
        otherAddress=otherAddress,
        ghcardnumber=ghCardNumber,
        nextOfKin=nextOfKin,
        ghCardImage=gh_card_image_data,
        memberImage=member_image_data,
        otherName=otherName,
        commonname=commonname,
        MaritalStatus=MaritalStatus,
        EducationLevel=EducationLevel,
        Town=Town,
        ruralOrUrban=ruralOrUrban,
    )

    db.add(member_model)
    db.commit()

    member_id = db.query(models.Members) \
        .order_by(desc(models.Members.member_id)) \
        .first()

    register_member(member_id.member_id, association_id, db)

    return "Member Registered Successfully"


@router.patch("/update")
async def create_memberinfo(member_id: int = Form(...),
                            firstname: str = Form(...),
                            middlename: Optional[str] = Form(None),
                            lastname: Optional[str] = Form(None),
                            dob: Optional[str] = Form(None),
                            gender: str = Form(...),
                            phone: Optional[str] = Form(None),
                            otherPhone: Optional[str] = Form(None),
                            address: Optional[str] = Form(None),
                            otherAddress: Optional[str] = Form(None),
                            ghCardNumber: Optional[str] = Form(None),
                            nextOfKin: Optional[str] = Form(None),
                            ghCardImage: Union[UploadFile, str, None] = None,
                            memberImage: Union[UploadFile, str, None] = None,
                            otherName: Optional[str] = Form(None),
                            commonname: Optional[str] = Form(None),
                            MaritalStatus: Optional[str] = Form(None),
                            EducationLevel: Optional[str] = Form(None),
                            Town: Optional[str] = Form(None),
                            ruralOrUrban: Optional[str] = Form(None),
                            user: dict = Depends(get_current_user),
                            db: Session = Depends(get_db)
                            ):
    if user is None:
        raise get_user_exception()

    if memberImage:
        memberImagee = memberImage.file.read()
    else:
        modelsImg = db.query(models.Members.memberImage).filter(models.Members.member_id == member_id).first()
        memberImagee = modelsImg.memberImage

    if ghCardImage:
        ghCardImagee = ghCardImage.file.read()
    else:
        ghCardImageh = db.query(models.Members).filter(models.Members.member_id == member_id).first()
        ghCardImagee = ghCardImageh.ghCardImage

    member_model = db.query(models.Members).filter(models.Members.member_id == member_id).first()

    if not member_model:
        raise HTTPException(status_code=404, detail="Member not found")

    # Update member_model with the new data
    member_model.firstname = firstname
    member_model.middlename = middlename
    member_model.lastname = lastname
    member_model.dob = dob
    member_model.gender = gender
    member_model.phone = phone
    member_model.otherPhone = otherPhone
    member_model.address = address
    member_model.otherAddress = otherAddress
    member_model.ghcardnumber = ghCardNumber
    member_model.nextOfKin = nextOfKin
    member_model.ghCardImage = ghCardImagee
    member_model.memberImage = memberImagee
    member_model.otherName = otherName
    member_model.commonname = commonname
    member_model.MaritalStatus = MaritalStatus
    member_model.EducationLevel = EducationLevel
    member_model.Town = Town
    member_model.ruralOrUrban = ruralOrUrban

    db.add(member_model)
    db.commit()

    return "Member updated successfully"


@router.post("/recieve/details")
def details(details: AssociationMembers,
            user: dict = Depends(get_current_user),
            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    m_id = details.member_id
    a_id = details.association_id
    r = register_member(m_id, a_id, db)

    return "Member Registered Successfully"


@router.post("/update/passbook_id")
def update_passbook_id(association_member_id: int = Form(...),
                       new_passbook_id: str = Form(...),
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    in_asso = db.query(models.Association).join(models.AssociationMembers, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.AssociationMembers.association_members_id == association_member_id) \
        .first()

    exist = db.query(models.AssociationMembers) \
        .filter(models.AssociationMembers.passbook_id == new_passbook_id,
                models.AssociationMembers.association_id == in_asso.association_id) \
        .first()
    if exist:
        return "Passbook id already exist in Association"
    else:
        db.query(models.AssociationMembers) \
            .filter(models.AssociationMembers.association_members_id == association_member_id) \
            .update({models.AssociationMembers.passbook_id: new_passbook_id})
        db.commit()
        return "Passbook id updated successfully"


def register_member(member_Id: int,
                    association_Id: int,
                    db: Session = Depends(get_db)):
    try:
        last_data = db.query(
            models.Association.association_name,
            models.AssociationMembers.association_members_id,
            models.AssociationMembers.passbook_id,
            models.AssociationType.association_type,
        ) \
            .select_from(models.AssociationMembers) \
            .join(
            models.Association,
            models.Association.association_id == models.AssociationMembers.association_id
        ) \
            .join(models.AssociationType,
                  models.AssociationType.associationtype_id == models.Association.association_type_id) \
            .filter(models.AssociationMembers.association_id == association_Id) \
            .order_by(desc(models.AssociationMembers.association_members_id)) \
            .first()

        if last_data is None:
            asso = (db.query(models.Association.association_name,
                             models.AssociationType.association_type)
                    .select_from(models.Association)
                    .join(models.AssociationType,
                          models.AssociationType.associationtype_id == models.Association.association_type_id) \
                    .filter(models.Association.association_id == association_Id).first())

            association_name = asso.association_name
            type_name = asso.association_type

            first_two_type_char = type_name[:1]
            first_two_characters = association_name[:2]
            passbook_id_suffix = 000 + 1
            new_passbook_id = f"{first_two_type_char}{first_two_characters}{passbook_id_suffix:03d}"

            associationMember_model = models.AssociationMembers(
                passbook_id=new_passbook_id,
                association_id=association_Id,
                members_id=member_Id
            )
            db.add(associationMember_model)
            db.commit()

        else:
            association_name = last_data[0]
            if last_data.passbook_id is None:
                pass
            else:
                last_passbook_id = last_data[2]

            first_one_type_char = last_data.association_type[:1]
            first_two_characters = association_name[:2]
            if last_data.passbook_id is None:
                passbook_id_suffix = 000
            else:
                passbook_id_suffix = last_passbook_id[3:]
            passbook_id_suffix_number = int(passbook_id_suffix) + 1
            new_passbook_id = f"{first_one_type_char}{first_two_characters}{passbook_id_suffix_number:03d}"

            associationMember_model = models.AssociationMembers(
                passbook_id=new_passbook_id,
                association_id=association_Id,
                members_id=member_Id
            )
            db.add(associationMember_model)
            db.commit()

        passbook_id = db.query(models.AssociationMembers) \
            .order_by(desc(models.AssociationMembers.association_members_id)) \
            .first()
        default_registration_account(member_Id=member_Id, association_member_id=passbook_id.association_members_id,
                                     db=db)
        return {f"Member Passbook Number is {passbook_id.association_members_id}"}

    except Exception as e:
        print(f"Here is the Exception {str(e)}")
        return {"error": str(e)}


def default_registration_account(member_Id: int,
                                 association_member_id: Optional[int],
                                 db: Session = Depends(get_db)):
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        account_coop_model = models.MemberSavingsAccount(
            savings_id=1,
            open_date=current_date,
            current_balance=-20,
            association_member_id=association_member_id,
            member_id=member_Id
        )
        account_dues_model = models.MemberSavingsAccount(
            savings_id=2,
            open_date=current_date,
            current_balance=0,
            association_member_id=association_member_id,
            member_id=member_Id
        )
        db.add(account_coop_model)
        db.add(account_dues_model)
        db.commit()
        return {"message": "Saved"}
    except Exception as e:
        print(f"Here is the Exception {str(e)}")
        return {"error": str(e)}


def default_registration_account_individuals(member_Id: int,
                                             db: Session = Depends(get_db)):
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        account_coop_model = models.MemberSavingsAccount(
            savings_id=1,
            open_date=current_date,
            current_balance=-20,
            association_member_id=None,
            member_id=member_Id
        )
        account_dues_model = models.MemberSavingsAccount(
            savings_id=2,
            open_date=current_date,
            current_balance=0,
            association_member_id=None,
            member_id=member_Id
        )
        db.add(account_coop_model)
        db.add(account_dues_model)
        db.commit()
        return {"message": "Saved"}
    except Exception as e:
        print(f"Here is the Exception {str(e)}")
        return {"error": str(e)}


@router.get("/form")
async def create_member_form(user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    Allassociations = db.query(models.Association).all()

    return Allassociations


@router.post("/memberassociation")
async def add_member_to_association(Association_id: int = Form(...),
                                    user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    memberID = db.query(models.Members) \
        .order_by(desc(models.Members.member_id)) \
        .first()
    asso = db.query(models.Association.association_name) \
        .filter(models.Association.association_id == Association_id) \
        .first()

    memberAssociatiion_model = models.AssociationMembers()
    memberAssociatiion_model.members_id = memberID.member_id
    memberAssociatiion_model.association_id = Association_id

    db.add(memberAssociatiion_model)
    db.commit()

    return f'Member Added to {asso} Association'


@router.get("/{member_id}")
async def get_one_member(
        member_id: int,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    member_info = (
        db.query(
            models.Members.lastname,
            models.Members.firstname,
            models.Members.middlename,
            models.Members.gender,
            models.Members.address,
            models.Members.phone,
            models.Members.dob,
            models.Members.ghcardnumber,
            models.Members.nextOfKin,
            models.Members.otherAddress,
            models.Members.otherPhone,
            models.Members.otherName,
            models.Members.commonname,
            models.Members.MaritalStatus,
            models.Members.EducationLevel,
            models.Members.Town,
            models.Members.ruralOrUrban
        ).filter(models.Members.member_id == member_id).first()
    )

    if not member_info:
        return {}
    (lastname, firstname,
     middlename, gender, address, phone,
     dob, ghcardnumber,
     nextOfKin, otherAddress, otherPhone,
     otherName, commonname, MaritalStatus,
     EducationLevel, Town, ruralOrUrban) = member_info

    dob_str = member_info.dob.strftime("%Y-%m-%d") if dob else None

    associationsJoined = (
        db.query(
            models.Association.association_name,
            models.Association.association_id,
            models.AssociationMembers.association_members_id,
        ).join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id)
        .filter(models.AssociationMembers.members_id == member_id)
        .all()
    )

    associationsJoined_list = [
        {"AssociationName": a.association_name, "Association_Id": a.association_id, "Psb": a.association_members_id} for
        a in
        associationsJoined]

    member_image_row = db.query(models.Members.memberImage).filter(models.Members.member_id == member_id).first()
    member_image = member_image_row.memberImage if member_image_row else None

    member_card_row = db.query(models.Members.ghCardImage).filter(models.Members.member_id == member_id).first()
    member_card = member_card_row.ghCardImage if member_card_row else None

    response = {
        "Member_Image": base64.b64encode(member_image).decode("utf-8") if member_image else None,
        "Last_name": lastname,
        "First_name": firstname,
        "Middle_name": middlename,
        "Gender": gender,
        "Address": address,
        "Phone": phone,
        "Date_Of_Birth": dob_str,
        "GhCard_Image": base64.b64encode(member_card).decode("utf-8") if member_card else None,
        "GhCard_Number": ghcardnumber,
        "Next_Of_Kin": nextOfKin,
        "Other_Address": otherAddress,
        "Other_Phone": otherPhone,
        "Other_Name": otherName,
        "Common_name": commonname,
        "MaritalStatus": MaritalStatus,
        "Member_Associations": associationsJoined_list,
        "EducationLevel": EducationLevel,
        "Town": Town,
        "ruralOrUrban": ruralOrUrban
    }

    return JSONResponse(content=response)


@router.get("/allmembers/{association_id}")
async def get_association_members(association_id: int,
                                  user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    members_info = (
        db.query(
            models.Association.association_id,
            models.AssociationMembers.association_members_id,
            models.AssociationMembers.passbook_id,
            models.Members.member_id,
            models.Members.firstname,
            models.Members.middlename,
            models.Members.lastname,
            models.Members.ghcardnumber,
            models.Members.phone,
            models.Members.commonname,
        )
        .select_from(models.Association)
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id)
        .join(models.Members, models.Members.member_id == models.AssociationMembers.members_id)
        .filter(models.Association.association_id == association_id)
        .order_by(desc(models.Members.member_id))
        .all()
    )

    response = []

    for row in members_info:
        (
            association_id,
            association_members_id,
            passbook_id,
            member_id,
            firstname,
            middlename,
            lastname,
            ghcardnumber,
            phone,
            commonname,
        ) = row

        response.append({
            "Association_id": association_id,
            "PassBook_id": association_members_id,
            "Original_pass": passbook_id,
            "Member_id": member_id,
            "Fullname": f"{firstname} {middlename} {lastname}",
            "GhCardNumber": ghcardnumber,
            "Phone": phone,
            "CommonName": commonname,
        })

    return response


@router.get("/passbooks/transfer/{association_id}")
async def get_association_passbooks(association_id: int,
                                    user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    yes = db.query(models.AssociationMembers.association_members_id,
                   models.Members.firstname,
                   models.Members.lastname,
                   models.Members.member_id) \
        .select_from(models.AssociationMembers) \
        .join(models.Members, models.Members.member_id == models.AssociationMembers.members_id) \
        .order_by(desc(models.AssociationMembers.association_members_id)) \
        .filter(models.AssociationMembers.association_id == association_id) \
        .all()
    return yes


@router.get("/everymember/{association_id}")
async def get_every_member(association_id: int,
                           user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    association_members = db.query(models.Members.member_id,
                                   models.Members.firstname,
                                   models.Members.lastname,
                                   models.Members.ghcardnumber,
                                   models.Association.association_name) \
        .join(models.AssociationMembers, models.AssociationMembers.members_id == models.Members.member_id) \
        .join(models.Association, models.AssociationMembers.association_id == models.Association.association_id) \
        .filter(models.AssociationMembers.association_id != association_id) \
        .order_by(desc(models.Members.member_id)) \
        .all()

    assoMembers = []

    for association_member in association_members:
        (
            member_id,
            firstname,
            lastname,
            ghcardnumber,
            association_name
        ) = association_member

        assoMembers.append({
            "member_id": member_id,
            "firstname": firstname,
            "lastname": lastname,
            "ghcardnumber": ghcardnumber,
            "association_name": association_name
        })

    individual_members = db.query(models.Members.member_id,
                                  models.Members.firstname,
                                  models.Members.lastname,
                                  models.Members.ghcardnumber) \
        .outerjoin(models.AssociationMembers, models.Members.member_id == models.AssociationMembers.members_id) \
        .filter(models.AssociationMembers.members_id.is_(None)) \
        .order_by(desc(models.Members.member_id)) \
        .all()
    indivMembers = []

    for individual_member in individual_members:
        (
            member_id,
            firstname,
            lastname,
            ghcardnumber
        ) = individual_member

        indivMembers.append({
            "Member_id": member_id,
            "Firstname": firstname,
            "Lastname": lastname,
            "GhCardNumber": ghcardnumber
        })

    return {"Association_members": assoMembers, "Individual_members": indivMembers}


@router.get("/all/emem")
async def get_all_members(user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    # Retrieve members who are in associations without duplicates
    member_info_kakra = db.query(
        models.Members.member_id,
        models.Members.firstname,
        models.Members.lastname,
        models.Members.middlename,
        models.Members.commonname,
        models.Members.address,
        models.Members.ghcardnumber,
        models.AssociationMembers.association_members_id,
        models.Association.association_name,
        models.AssociationMembers.passbook_id,
    ) \
        .outerjoin(models.AssociationMembers, models.AssociationMembers.members_id == models.Members.member_id) \
        .join(models.Association, models.AssociationMembers.association_id == models.Association.association_id) \
        .order_by(desc(models.Members.member_id)) \
        .all()

    seen_member_ids = set()
    members_in_associations = []

    for member_info_kakra_nu in member_info_kakra:
        (
            member_id,
            firstname,
            lastname,
            middlename,
            commonname,
            address,
            ghcardnumber,
            association_members_id,
            association_name,
            passbook_id,
        ) = member_info_kakra_nu

        if member_id not in seen_member_ids:
            seen_member_ids.add(member_id)
            members_in_associations.append({
                "member_id": member_id,
                "firstname": firstname,
                "lastname": lastname,
                "middlename": middlename,
                "commonname": commonname,
                "address": address,
                "ghcardnumber": ghcardnumber,
                "association_members_id": association_members_id,
                "association_name": association_name,
                "passbook_id": passbook_id
            })

    # Retrieve members who are not in any association
    individual_members = db.query(
        models.Members.member_id,
        models.Members.firstname,
        models.Members.lastname,
        models.Members.middlename,
        models.Members.commonname,
        models.Members.address,
        models.Members.ghcardnumber
    ) \
        .filter(models.Members.member_id.notin_(
        db.query(models.AssociationMembers.members_id)
    )) \
        .order_by(desc(models.Members.member_id)) \
        .all()

    individual_members_list = []

    for individual_member in individual_members:
        (
            member_id,
            firstname,
            lastname,
            middlename,
            commonname,
            address,
            ghcardnumber,
        ) = individual_member

        individual_members_list.append({
            "member_id": member_id,
            "firstname": firstname,
            "lastname": lastname,
            "middlename": middlename,
            "commonname": commonname,
            "address": address,
            "ghcardnumber": ghcardnumber,
        })

    return {
        "Association_Members": members_in_associations,
        "Individual_Members": individual_members_list
    }


@router.get("/member/passbook_id/{association_member_id}")
async def get_member_passbook_id(association_member_id: int,
                                 user: dict = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    association_initials = db.query(models.Association.association_name,
                                    models.AssociationType.association_type) \
        .select_from(models.Association) \
        .join(models.AssociationType, models.AssociationType.associationtype_id == models.Association.association_type_id) \
        .join(models.AssociationMembers, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.AssociationMembers.association_members_id == association_member_id) \
        .order_by(desc(models.AssociationMembers.association_members_id)) \
        .first()
    type_initials = association_initials.association_type[:1]
    asso_intitials = association_initials.association_name[:2]

    initials = f"{type_initials}{asso_intitials}"

    passbook_id = db.query(models.AssociationMembers).filter(
        models.AssociationMembers.association_members_id == association_member_id).first()

    return {"pass_id": passbook_id.passbook_id, "initials": initials}


@router.delete("/{member_id}")
async def delete_member(member_id: int,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    member_model = db.query(models.Members) \
        .filter(models.Members.member_id == member_id) \
        .first()
    if member_model is None:
        raise HTTPException(status_code=404, detail="Member not found")

    db.query(models.Members) \
        .filter(models.Members.member_id == member_id) \
        .delete()
    db.commit()
    return "Deleted Successfully"
