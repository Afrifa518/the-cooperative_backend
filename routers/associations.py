import sys

sys.path.append("../..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session, aliased
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/association",
    tags=["association"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Association(BaseModel):
    association_name: str
    association_type_id: int
    community_name: str
    open_date: str
    facilitator_userid: int
    association_email: Optional[str]
    cluster_office: Optional[str]
    staff_userid: int
    created_by: Optional[int]


class AssociationType(BaseModel):
    association_type: str
    accepted_forms: str
    open_date: str


@router.post("/create/type")
async def create_association_type(assotype: AssociationType,
                                  user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    type_model = models.AssociationType()
    type_model.association_type = assotype.association_type
    type_model.accepted_forms = assotype.accepted_forms
    type_model.open_date = assotype.open_date

    db.add(type_model)
    db.flush()
    db.commit()

    return "Setup Complete"


@router.get("/form/")
async def create_association_form(user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    Assotype = db.query(models.AssociationType).all()
    facilitator = db.query(models.Users).all()
    return {'Assotype': Assotype}, {'facilitator': facilitator}


@router.post("/create")
async def create_association(association: Association,
                             user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    association_model = models.Association()
    association_model.association_name = association.association_name
    association_model.association_type_id = association.association_type_id
    association_model.community_name = association.community_name
    association_model.open_date = association.open_date
    association_model.facilitator_userid = association.facilitator_userid
    association_model.association_email = association.association_email
    association_model.cluster_office = association.cluster_office
    association_model.staff_userid = association.staff_userid
    association_model.created_by = user.get('id')

    db.add(association_model)
    db.commit()

    return "Created Successfully"


@router.put("/{association_id}")
async def update_association(association_id: int,
                             association: Association,
                             user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    association_model = db.query(models.Association) \
        .filter(models.Association.association_id == association_id) \
        .first()

    if association_model is None:
        raise HTTPException(status_code=404, detail="Association not found")

    association_model.association_name = association.association_name
    association_model.association_type_id = association.association_type_id
    association_model.community_name = association.community_name
    association_model.open_date = association.open_date
    association_model.facilitator_userid = association.facilitator_userid
    association_model.association_email = association.association_email
    association_model.cluster_office = association.cluster_office
    association_model.staff_userid = association.staff_userid
    association_model.created_by = association.created_by

    db.add(association_model)
    db.commit()

    return f"{association.association_name} Updated Successfully"


@router.delete("/{association_id}")
async def delete_association(association_id: int,
                             user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    association_model = db.query(models.Association) \
        .filter(models.Association.association_id == association_id) \
        .first()
    if association_model is None:
        raise HTTPException(status_code=404, detail="Association not found")

    db.query(models.Association) \
        .filter(models.Association.association_id == association_id) \
        .delete()
    db.commit()
    return "Deleted Successfully"


@router.get("/")
async def all_associations(db: Session = Depends(get_db)):
    associations = db.query(models.Association, models.AssociationMembers.association_members_id,
                            models.AssociationType.association_type, models.Users.username) \
        .join(models.AssociationType,
              models.Association.association_type_id == models.AssociationType.associationtype_id) \
        .join(models.Users, models.Users.id == models.Association.facilitator_userid) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_id == models.Association.association_id) \
        .all()

    results = []
    for association, association_type, association_members_id, facilitator in associations:
        results.append({
            "Association_id": association.association_id,
            "Association_name": association.association_name,
            "community_name": association.community_name,
            "association_cluster": association.cluster_office,
            "association_members": association_members_id,
            "open_date": association.open_date,
            "Association_Type": association_type,
            "Facilitator_username": facilitator,
        })

    return results


@router.get("/{association_id}")
async def get_one_association(
        association_id: int,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    association_info = (
        db.query(
            models.Association.association_id,
            models.Association.community_name,
            models.Association.open_date,
            models.Association.association_name,
            models.AssociationType.association_type,
            models.Users.username,
        )
        .join(models.AssociationType,
              models.Association.association_type_id == models.AssociationType.associationtype_id)
        .join(models.Users, models.Users.id == models.Association.facilitator_userid)
        .filter(models.Association.association_id == association_id)
        .first()
    )

    if not association_info:
        return {}

    association_id, community_name, open_date, association_name, association_type, facilitator_username = association_info

    members = (
        db.query(
            models.Members.member_id,
            models.Members.firstname,
            models.Members.middlename,
            models.Members.lastname,
            models.AssociationMembers.association_members_id
        )
        .join(models.AssociationMembers, models.Members.member_id == models.AssociationMembers.members_id)
        .filter(models.AssociationMembers.association_id == association_id)
        .all()
    )

    # Convert the list of members into a list of dictionaries
    member_list = [
        {"Name": f"{m.firstname} {m.middlename} {m.lastname}", "id": m.member_id,
         "passbookId": m.association_members_id}
        for m in members
    ]

    response = {
        "Association_id": association_id,
        "Association_name": association_name,
        "Association_Type": association_type,
        "Facilitator_username": facilitator_username,
        "Members": member_list,
        "open_date": open_date,
        "community_name": community_name,
    }

    return response


@router.get("/specified/{association_id}")
async def get_one_association(
        association_id: int,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    # users_facilitator = aliased(models.Users)
    # users_staff_assigned = aliased(models.Users)
    # users_created_by = aliased(models.Users)

    association_info = (
        db.query(
            models.Association.association_id,
            models.Association.community_name,
            models.Association.open_date,
            models.Association.association_name,
            models.Association.association_email,
            models.Association.cluster_office,
            models.Association.association_type_id,
            models.Association.created_by,
            models.Association.facilitator_userid,
            models.Association.staff_userid,
            models.AssociationType.association_type,
            models.Users.username,
        )
        .select_from(models.Association)
        .join(models.AssociationType,
              models.Association.association_type_id == models.AssociationType.associationtype_id)
        .join(models.Users, models.Users.id == models.Association.facilitator_userid)
        .filter(models.Association.association_id == association_id)
        .first()
    )

    if not association_info:
        return {}

    staf = (
        db.query(models.Users.username)
        .join(models.Association, models.Users.id == models.Association.staff_userid)
        .filter(models.Association.association_id == association_id)
        .first()
    )

    staf_username = staf.username if staf else None

    creator = (
        db.query(models.Users.username)
        .join(models.Association, models.Users.id == models.Association.created_by)
        .filter(models.Association.association_id == association_id)
        .first()
    )

    creator_username = creator.username if creator else None

    (
        association_id,
        community_name,
        open_date,
        association_name,
        association_email,
        cluster_office,
        association_type_id,
        created_by,
        facilitator_userid,
        staff_userid,
        association_type,
        facilitator_username,
    ) = association_info

    members = (
        db.query(
            models.Members.member_id,
            models.Members.firstname,
            models.Members.middlename,
            models.Members.lastname,
            models.AssociationMembers.association_members_id
        )
        .join(models.AssociationMembers, models.Members.member_id == models.AssociationMembers.members_id)
        .filter(models.AssociationMembers.association_id == association_id)
        .all()
    )

    member_list = [
        {"Name": f"{m.firstname} {m.middlename} {m.lastname}", "id": m.member_id,
         "passbookId": m.association_members_id}
        for m in members
    ]

    response = {
        "Association_id": association_id,
        "Association_name": association_name,
        "Association_Type": association_type,
        "Facilitator_id": facilitator_userid,
        "Association_type_id": association_type_id,
        "Created_by": created_by,
        "Staff_id": staff_userid,
        "Facilitator_username": facilitator_username,
        "Members": member_list,
        "open_date": open_date,
        "community_name": community_name,
        "association_email": association_email,
        "cluster_office": cluster_office,
    }

    response.update({
        "Staff_Assigned_username": staf_username,
        "Created_by_username": creator_username
    })

    return response


@router.get("/types/")
async def get_all_association_types(user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    association_types = db.query(models.AssociationType).all()
    return association_types


@router.get("/types/{types_id}")
async def get_association_typ_info(types_id: int,
                                   user: dict = Depends(get_current_user),
                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    association_type_info = db.query(models.AssociationType) \
        .filter(models.AssociationType.associationtype_id == types_id) \
        .first()
    association_of_type = db.query(models.Association) \
        .filter(models.Association.association_type_id == types_id) \
        .all()

    return association_type_info, association_of_type


@router.get("/loans/info/{association_id}")
async def get_requested_loans_in_association(association_id: int,
                                             user: dict = Depends(get_current_user),
                                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    loans = db.query(models.LoansTransaction) \
        .select_from(models.Association) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.Members,
              models.Members.member_id == models.AssociationMembers.members_id) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.LoansTransaction,
              models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .filter(models.LoansTransaction.status == 'Requested',
                models.AssociationMembers.association_id == association_id) \
        .all()

    results = []
    for loan in loans:
        results.append({
            "Transaction_id": loan.transaction_id,
            "Amount": loan.amount,
            "Prepared_by": loan.prepared_by.username,
            "Narration": loan.narration,
            "Transaction_date": loan.transaction_date,
            "Member_name": loan.loan_account.membersowwn.firstname + " " + loan.loan_account.membersowwn.lastname,
            "Member_id": loan.loan_account.membersowwn.member_id
        })

    return results


@router.get("/loans/approved/{association_id}")
async def get_approved_loans_in_association(association_id: int,
                                            user: dict = Depends(get_current_user),
                                            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    loans = db.query(models.LoansTransaction) \
        .select_from(models.Association) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.Members,
              models.Members.member_id == models.AssociationMembers.members_id) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.LoansTransaction,
              models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .filter(models.LoansTransaction.status == 'Approved',
                models.AssociationMembers.association_id == association_id) \
        .all()

    results = []
    for loan in loans:
        results.append({
            "Transaction_id": loan.transaction_id,
            "Amount": loan.amount,
            "Prepared_by": loan.prepared_by.username,
            "Narration": loan.narration,
            "Transaction_date": loan.transaction_date,
            "Member_name": loan.loan_account.membersowwn.firstname + " " + loan.loan_account.membersowwn.lastname,
            "Member_id": loan.loan_account.membersowwn.member_id
        })

    return results


@router.get("/loans/disbursed/{association_id}")
async def get_disbursed_loans_in_association(association_id: int,
                                             user: dict = Depends(get_current_user),
                                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    loans = db.query(models.LoansTransaction) \
        .select_from(models.Association) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.Members,
              models.Members.member_id == models.AssociationMembers.members_id) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.LoansTransaction,
              models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .filter(models.LoansTransaction.status == 'Disbursed',
                models.AssociationMembers.association_id == association_id) \
        .all()

    results = []
    for loan in loans:
        results.append({
            "Transaction_id": loan.transaction_id,
            "Amount": loan.amount,
            "Prepared_by": loan.prepared_by.username,
            "Narration": loan.narration,
            "Transaction_date": loan.transaction_date,
            "Member_name": loan.loan_account.membersowwn.firstname + " " + loan.loan_account.membersowwn.lastname,
            "Member_id": loan.loan_account.membersowwn.member_id
        })

    return results
