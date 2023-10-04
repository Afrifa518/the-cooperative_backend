import sys
from datetime import datetime

from sqlalchemy import desc, func, select

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
            "Repayment_starts": loan.repayment_starts,
            "Repayment_ends": loan.repayment_ends,
            "Member_name": loan.loan_account.membersowwn.firstname + " " + loan.loan_account.membersowwn.lastname,
            "Member_id": loan.loan_account.membersowwn.member_id
        })

    return results


@router.get("/passbook/{association_id}")
async def get_association_passbook_info(association_id: int,
                                        user: dict = Depends(get_current_user),
                                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    all_savings_acc = db.query(models.MemberSavingsAccount.current_balance,
                               models.MemberSavingsAccount.member_id,
                               models.MemberSavingsAccount.association_member_id,
                               models.MemberSavingsAccount.id,
                               models.SavingsAccount.account_name,
                               models.Members.firstname,
                               models.Members.lastname) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberSavingsAccount,
              models.MemberSavingsAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
        .filter(models.Association.association_id == association_id) \
        .order_by(desc(models.AssociationMembers.association_members_id)) \
        .all()

    all_loans_acc = db.query(models.MemberLoanAccount.current_balance,
                             models.MemberLoanAccount.member_id,
                             models.MemberLoanAccount.association_member_id,
                             models.MemberLoanAccount.id,
                             models.LoanAccount.account_name,
                             models.Members.firstname,
                             models.Members.lastname) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
        .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
        .filter(models.Association.association_id == association_id) \
        .order_by(desc(models.AssociationMembers.association_members_id)) \
        .all()

    # print(all_loans_acc)

    all_shares_acc = db.query(models.MemberShareAccount.current_balance,
                              models.MemberShareAccount.member_id,
                              models.MemberShareAccount.id,
                              models.MemberShareAccount.association_member_id,
                              models.ShareAccount.account_name,
                              models.Members.firstname,
                              models.Members.lastname) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberShareAccount,
              models.MemberShareAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
        .filter(models.Association.association_id == association_id) \
        .order_by(desc(models.AssociationMembers.association_members_id)) \
        .all()

    # all_commodity_acc = db.query(models.MemberCommodityAccount.cash_value,
    #                              models.MemberCommodityAccount.member_id,
    #                              models.MemberCommodityAccount.id,
    #                              models.MemberCommodityAccount.association_member_id,
    #                              models.CommodityAccount.warehouse,
    #                              models.Members.firstname,
    #                              models.Members.lastname) \
    #     .select_from(models.Association) \
    #     .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
    #     .join(models.MemberCommodityAccount,
    #           models.MemberCommodityAccount.association_member_id == models.AssociationMembers.association_members_id) \
    #     .join(models.CommodityAccount, models.CommodityAccount.id == models.MemberCommodityAccount.commodity_id) \
    #     .join(models.Members, models.Members.member_id == models.MemberCommodityAccount.member_id) \
    #     .filter(models.Association.association_id == association_id) \
    #     .order_by(desc(models.AssociationMembers.association_members_id)) \
    #     .all()

    current_datetime = datetime.now()

    start_of_day = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Savings
    todays_savings_accounts_transactions = db.query(models.Members.firstname,
                                                    models.MemberSavingsAccount.id,
                                                    models.Members.lastname,
                                                    models.Members.member_id,
                                                    models.TransactionType.transactiontype_name,
                                                    models.SavingsTransaction.amount,
                                                    models.SavingsTransaction.transaction_date,
                                                    models.SavingsTransaction.narration,
                                                    models.Users.username) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberSavingsAccount,
              models.MemberSavingsAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
        .join(models.SavingsTransaction, models.SavingsTransaction.savings_acc_id == models.MemberSavingsAccount.id) \
        .join(models.TransactionType,
              models.SavingsTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users, models.Users.id == models.SavingsTransaction.prep_by) \
        .filter(models.Association.association_id == association_id,
                models.SavingsTransaction.transaction_date >= start_of_day,
                models.SavingsTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    savings_accounts_transactions = db.query(models.Members.firstname,
                                             models.MemberSavingsAccount.id,
                                             models.Members.lastname,
                                             models.Members.member_id,
                                             models.TransactionType.transactiontype_name,
                                             models.SavingsTransaction.amount,
                                             models.SavingsTransaction.transaction_date,
                                             models.SavingsTransaction.narration,
                                             models.Users.username) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberSavingsAccount,
              models.MemberSavingsAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
        .join(models.SavingsTransaction, models.SavingsTransaction.savings_acc_id == models.MemberSavingsAccount.id) \
        .join(models.TransactionType,
              models.SavingsTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users, models.Users.id == models.SavingsTransaction.prep_by) \
        .filter(models.Association.association_id == association_id) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    # Loans
    todays_loan_accounts_transactions = db.query(models.Members.firstname,
                                                 models.MemberLoanAccount.id,
                                                 models.Members.lastname,
                                                 models.Members.member_id,
                                                 models.TransactionType.transactiontype_name,
                                                 models.LoansTransaction.amount,
                                                 models.LoansTransaction.transaction_date,
                                                 models.LoansTransaction.narration,
                                                 models.Users.username) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
        .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
        .join(models.LoansTransaction, models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .join(models.TransactionType,
              models.LoansTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users, models.Users.id == models.LoansTransaction.prep_by) \
        .filter(models.Association.association_id == association_id,
                models.LoansTransaction.transaction_date >= start_of_day,
                models.LoansTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .all()

    loan_accounts_transactions = db.query(models.Members.firstname,
                                          models.MemberLoanAccount.id,
                                          models.Members.lastname,
                                          models.Members.member_id,
                                          models.TransactionType.transactiontype_name,
                                          models.LoansTransaction.amount,
                                          models.LoansTransaction.transaction_date,
                                          models.LoansTransaction.narration,
                                          models.Users.username) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
        .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
        .join(models.LoansTransaction, models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .join(models.TransactionType,
              models.LoansTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users, models.Users.id == models.LoansTransaction.prep_by) \
        .filter(models.Association.association_id == association_id) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .all()

    # Shares
    todays_share_accounts_transactions = db.query(models.Members.firstname,
                                                  models.MemberShareAccount.id,
                                                  models.Members.lastname,
                                                  models.Members.member_id,
                                                  models.TransactionType.transactiontype_name,
                                                  models.SharesTransaction.amount,
                                                  models.SharesTransaction.transaction_date,
                                                  models.SharesTransaction.narration,
                                                  models.Users.username) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberShareAccount,
              models.MemberShareAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
        .join(models.SharesTransaction, models.SharesTransaction.shares_acc_id == models.MemberShareAccount.id) \
        .join(models.TransactionType,
              models.SharesTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users, models.Users.id == models.SharesTransaction.prep_by) \
        .filter(models.Association.association_id == association_id,
                models.SharesTransaction.transaction_date >= start_of_day,
                models.SharesTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.SharesTransaction.transaction_id)) \
        .all()

    share_accounts_transactions = db.query(models.Members.firstname,
                                           models.MemberShareAccount.id,
                                           models.Members.lastname,
                                           models.Members.member_id,
                                           models.TransactionType.transactiontype_name,
                                           models.SharesTransaction.amount,
                                           models.SharesTransaction.transaction_date,
                                           models.SharesTransaction.narration,
                                           models.Users.username) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.MemberShareAccount,
              models.MemberShareAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
        .join(models.SharesTransaction, models.SharesTransaction.shares_acc_id == models.MemberShareAccount.id) \
        .join(models.TransactionType,
              models.SharesTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users, models.Users.id == models.SharesTransaction.prep_by) \
        .filter(models.Association.association_id == association_id) \
        .order_by(desc(models.SharesTransaction.transaction_id)) \
        .all()

    return {"All_Savings_account": all_savings_acc,
            "All_Loans_account": all_loans_acc,
            "All_Shares_acount": all_shares_acc,
            # "All_Commodity_account": all_commodity_acc,
            "Todays_Savings_Transactions": todays_savings_accounts_transactions,
            "Savings_Transactions": savings_accounts_transactions,
            "Todays_Loans_Transactions": todays_loan_accounts_transactions,
            "Loans_Transactions": loan_accounts_transactions,
            "Todays_Shares_Transactions": todays_share_accounts_transactions,
            "Shares_Transactions": share_accounts_transactions,
            }


@router.get("/goto/form")
async def get_all_associations_id_for_mass_deposit(user: dict = Depends(get_current_user),
                                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    all_associations = db.query(models.Association.association_id,
                    models.Association.association_name,
                    models.AssociationType.association_type).select_from(models.Association) \
        .join(models.AssociationType,
              models.AssociationType.associationtype_id == models.Association.association_type_id) \
        .all()
    return {"All_Associations": all_associations}
