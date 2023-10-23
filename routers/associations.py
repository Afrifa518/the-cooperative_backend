import sys
from datetime import datetime

from sqlalchemy import desc, not_, func, select, union_all, case, literal_column

sys.path.append("../..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session, aliased
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_exception
from datetime import datetime, timedelta

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
    society_id: int


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
    type_model.society_id = assotype.society_id

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


@router.post("/create/society/{society}")
async def create_society(society: str,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    mod = models.Society()
    mod.society = society

    db.add(mod)
    db.commit()



    return "New Society Created"


@router.post("/update/society")
async def change_society_name(society_id: int = Form(...),
                              new_name: str = Form(...),
                              user: dict = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    update_data = {models.Society.society: new_name}
    db.query(models.Society).filter(models.Society.id == society_id).update(update_data)
    db.commit()
    return "Updated Successfully"


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


@router.get("/types/{society_id}")
async def get_all_association_types(society_id: int,
                                    user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    association_types = db.query(models.AssociationType).filter(models.AssociationType.society_id == society_id).all()
    society = db.query(models.Society).filter(models.Society.id == society_id).first()
    return {"types": association_types, "place": society}


@router.get("/societies/")
async def get_all_societies(user: dict = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    societies = db.query(models.Society).all()

    return {"Society": societies}


@router.get("/type/{types_id}")
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


@router.get("/passbook/info/{association_id}")
async def get_association_passbook_info_yeah(association_id: int,
                                             user: dict = Depends(get_current_user),
                                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    tday = datetime.now()
    today = tday.strftime("%Y-%m-%d")
    yesterday_date = datetime.now() - timedelta(days=1)
    yesterday = yesterday_date.strftime("%Y-%m-%d")
    # print(yestaday)
    seen_ids = set()
    tra = []
    todayy = db.query(models.CashAssociationAccount).filter(models.CashAssociationAccount.date == today,
                                                            models.CashAssociationAccount.association_id == association_id).first()

    yestaday = db.query(models.CashAssociationAccount).filter(
        models.CashAssociationAccount.association_id == association_id,
        models.CashAssociationAccount.date < today).first()

    data = {}

    if todayy.cash_savings_bal is None:
        data["id"] = yestaday.id
        data["Starting_Savings"] = yestaday.cash_savings_bal
        data["Current_Savings"] = 0
        data["Addition_Subtraction_in_Savings"] = 0 + yestaday.cash_savings_bal
    else:
        data["id"] = todayy.id
        data["Starting_Savings"] = yestaday.cash_savings_bal
        data["Current_Savings"] = todayy.cash_savings_bal
        data["Addition_Subtraction_in_Savings"] = todayy.cash_savings_bal + yestaday.cash_savings_bal

    if todayy.cash_loans_bal is None:
        data["Starting_Loans"] = yestaday.cash_loans_bal
        data["Current_Loans"] = 0
        data["Addition_Subtraction_in_Loans"] = 0 + yestaday.cash_loans_bal
    else:
        data["Starting_Loans"] = yestaday.cash_loans_bal
        data["Current_Loans"] = todayy.cash_loans_bal
        data["Addition_Subtraction_in_Loans"] = todayy.cash_loans_bal + yestaday.cash_loans_bal

    if todayy.cash_shares_bal is None:
        data["Starting_Shares"] = yestaday.cash_shares_bal
        data["Current_Shares"] = 0
        data["Addition_Subtraction_in_Shares"] = 0 + yestaday.cash_shares_bal
    else:
        data["Starting_Shares"] = yestaday.cash_shares_bal
        data["Current_Shares"] = todayy.cash_shares_bal
        data["Addition_Subtraction_in_Shares"] = todayy.cash_shares_bal + yestaday.cash_shares_bal

    if todayy.withdrawal_value is None:
        data["Starting_Withdraws"] = yestaday.withdrawal_value
        data["Current_Withdraws"] = 0
        data["Addition_Subtraction_in_Withdraws"] = 0 + yestaday.withdrawal_value
    else:
        data["Starting_Withdraws"] = yestaday.withdrawal_value
        data["Current_Withdraws"] = todayy.withdrawal_value
        data["Addition_Subtraction_in_Withdraws"] = todayy.withdrawal_value + yestaday.withdrawal_value

    if todayy.transfers_value is None:
        data["Starting_Transfers"] = yestaday.transfers_value
        data["Current_Transfers"] = 0
        data["Addition_Subtraction_in_Transfers"] = 0 + yestaday.transfers_value
    else:
        data["Starting_Transfers"] = yestaday.transfers_value
        data["Current_Transfers"] = todayy.transfers_value
        data["Addition_Subtraction_in_Transfers"] = todayy.transfers_value + yestaday.transfers_value

    tra.append(data)
    return tra


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


@router.get("/cash/settings/{association_id}")
async def set_cash_account_balances(association_id: int,
                                    user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    current_datetime = datetime.now()

    start_of_day = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)

    today_date = current_datetime.strftime('%Y-%m-%d')

    # Today's Savings
    todays_savings_accounts_transactions = db.query(models.Members.firstname,
                                                    models.MemberSavingsAccount.id,
                                                    models.Members.lastname,
                                                    models.Members.member_id,
                                                    models.TransactionType.transactiontype_name,
                                                    models.SavingsTransaction.amount,
                                                    models.SavingsTransaction.transactiontype_id,
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
                models.SavingsTransaction.transaction_date <= end_of_day,
                models.TransactionType.transactiontype_name == "Deposit",
                not_(models.SavingsTransaction.narration.like("%Transfered to%")),
                not_(models.SavingsTransaction.narration.like("%Received from%"))
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    todays_savings_accounts_withdrawals = db.query(models.Members.firstname,
                                                   models.MemberSavingsAccount.id,
                                                   models.Members.lastname,
                                                   models.Members.member_id,
                                                   models.TransactionType.transactiontype_name,
                                                   models.SavingsTransaction.amount,
                                                   models.SavingsTransaction.transactiontype_id,
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
                models.SavingsTransaction.transaction_date <= end_of_day,
                models.TransactionType.transactiontype_name == "Withdraw",
                not_(models.SavingsTransaction.narration.like("%Transferred to%")),
                not_(models.SavingsTransaction.narration.like("%Received from%"))
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    todays_savings_accounts_transfers = db.query(models.Members.firstname,
                                                 models.MemberSavingsAccount.id,
                                                 models.Members.lastname,
                                                 models.Members.member_id,
                                                 models.TransactionType.transactiontype_name,
                                                 models.SavingsTransaction.amount,
                                                 models.SavingsTransaction.transactiontype_id,
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
                models.SavingsTransaction.transaction_date <= end_of_day,
                (models.SavingsTransaction.narration.like("%Transferred to:%")) |
                (models.SavingsTransaction.narration.like("%Received from:%"))
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    # Today's Loans
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
                models.LoansTransaction.transactiontype_id == 1,
                models.LoansTransaction.transaction_date >= start_of_day,
                models.LoansTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .all()

    # Today shares
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

    today_savings_total = sum(transaction.amount for transaction in todays_savings_accounts_transactions)
    today_loans_total = sum(transaction.amount for transaction in todays_loan_accounts_transactions)
    today_share_total = sum(transaction.amount for transaction in todays_share_accounts_transactions)
    today_withdrawals_total = sum(transaction.amount for transaction in todays_savings_accounts_withdrawals)
    todays_savings_accounts_transfers_total = sum(
        transaction.amount for transaction in todays_savings_accounts_transfers)
    total_cash_value = (
            today_savings_total + today_loans_total + today_share_total + today_withdrawals_total + todays_savings_accounts_transfers_total)

    today = db.query(models.CashAssociationAccount) \
        .filter(models.CashAssociationAccount.date == today_date,
                models.CashAssociationAccount.association_id == association_id) \
        .first()
    if today:
        today.cash_savings_bal = today_savings_total
        today.cash_loans_bal = today_loans_total
        today.cash_shares_bal = today_share_total
        today.cash_value = total_cash_value
        today.withdrawal_value = today_withdrawals_total
        today.transfers_value = todays_savings_accounts_transfers_total
        db.commit()
    else:
        create_today = models.CashAssociationAccount(
            date=today_date,
            cash_savings_bal=today_savings_total,
            cash_loans_bal=today_loans_total,
            cash_shares_bal=today_share_total,
            association_id=association_id,
            cash_value=total_cash_value,
            withdrawal_value=today_withdrawals_total,
            transfers_value=todays_savings_accounts_transfers_total
        )
        db.add(create_today)
        db.commit()
    momo_details = MomoTransactions(momo_bal=0.00, association_id=association_id)
    await set_momo_account_balances(momo_details, user=user, db=db)


class MomoTransactions(BaseModel):
    momo_bal: Optional[float]
    association_id: int


@router.post("/momo/account")
async def set_momo_account_balances(momo_details: MomoTransactions,
                                    user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_date = datetime.now()
    today_date = current_date.strftime('%Y-%m-%d')

    today = db.query(models.MomoAccountAssociation) \
        .filter(models.MomoAccountAssociation.date == today_date,
                models.MomoAccountAssociation.association_id == momo_details.association_id) \
        .first()
    if today:
        today.momo_bal = momo_details.momo_bal
        # today.momo_loans_bal = momo_details.momo_loans_bal
        # today.momo_shares_bal = momo_details.momo_shares_bal
        db.commit()
    else:
        create_momo_details = models.MomoAccountAssociation(
            date=today_date,
            momo_bal=momo_details.momo_bal,
            # momo_loans_bal=momo_details.momo_loans_bal,
            # momo_shares_bal=momo_details.momo_shares_bal,
            association_id=momo_details.association_id,
            status="Not Reconciled",
            button="Reconcile"
        )
        db.add(create_momo_details)
        db.commit()

    return "Saved"


class Datara(BaseModel):
    status: str
    note: Optional[str]
    momo_id: int
    message: Optional[str]


@router.get("/reconciled/note/{momo_id}")
async def get_reconciled_note(momo_id: int,
                              user: dict = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    nt = db.query(models.ReconciliationNote).filter(models.ReconciliationNote.momo_id == momo_id).first()

    chats = db.query(models.ReconciliationChats.message,
                     models.Users.username) \
        .select_from(models.ReconciliationChats) \
        .join(models.Users,
              models.Users.id == models.ReconciliationChats.from_id) \
        .filter(models.ReconciliationChats.to_recon_id == momo_id) \
        .order_by(models.ReconciliationChats.id) \
        .all()

    if nt:
        return {"Note": nt.note, "Chats": chats}
    else:
        return {"Chats": chats}


@router.post("/edit/reconciliation")
async def edit_reconciliations(data: Datara,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    changer = db.query(models.MomoAccountAssociation) \
        .filter(models.MomoAccountAssociation.id == data.momo_id) \
        .first()
    changer.status = data.status
    db.commit()
    nt = db.query(models.ReconciliationNote).filter(models.ReconciliationNote.momo_id == data.momo_id).first()
    if nt:
        nt.note = data.note
    else:
        notet = models.ReconciliationNote(
            note=data.note,
            momo_id=data.momo_id
        )
        db.add(notet)
        db.commit()

    mesg = models.ReconciliationChats(
        from_id=user.get("id"),
        to_recon_id=data.momo_id,
        message=data.message
    )
    db.add(mesg)
    db.commit()


class MOButoon(BaseModel):
    momo_id: int
    button: str


@router.post("/set/button")
async def set_button(dantn: MOButoon,
                     user: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    moddes = db.query(models.MomoAccountAssociation) \
        .filter(models.MomoAccountAssociation.id == dantn.momo_id) \
        .first()
    moddes.button = dantn.button
    db.commit()


@router.get("/cash/view/{association_id}")
async def get_cash_account_balance(association_id: int,
                                   user: dict = Depends(get_current_user),
                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    current_date = datetime.now()
    today_date = current_date.strftime('%Y-%m-%d')

    comparing_table = []

    today_cash_amounts = db.query(models.CashAssociationAccount.date,
                                  models.CashAssociationAccount.id,
                                  models.CashAssociationAccount.cash_savings_bal,
                                  models.CashAssociationAccount.cash_loans_bal,
                                  models.CashAssociationAccount.cash_shares_bal,
                                  models.CashAssociationAccount.cash_value,
                                  models.CashAssociationAccount.transfers_value,
                                  models.CashAssociationAccount.withdrawal_value
                                  ) \
        .filter(models.CashAssociationAccount.association_id == association_id,
                models.CashAssociationAccount.date == today_date) \
        .first()

    today_ecash_amounts = db.query(models.MomoAccountAssociation.date,
                                   models.MomoAccountAssociation.id,
                                   models.MomoAccountAssociation.momo_bal,
                                   ) \
        .filter(models.MomoAccountAssociation.association_id == association_id,
                models.MomoAccountAssociation.date == today_date) \
        .first()

    if today_ecash_amounts:
        comparing_table.append({
            "Id": today_cash_amounts.id,
            "Date": today_cash_amounts.date,
            "Transfers": today_cash_amounts.transfers_value,
            "Withdraws": today_cash_amounts.withdrawal_value,
            "Cash_Bal": today_cash_amounts.cash_value,
            "Ecash_Bal": today_ecash_amounts.momo_bal,
            "difference": round(today_cash_amounts.cash_savings_bal - today_ecash_amounts.momo_bal, 2),
        })
    else:
        comparing_table.append({
            "Id": today_cash_amounts.id,
            "Date": today_cash_amounts.date,
            "Transfers": today_cash_amounts.transfers_value,
            "Withdraws": today_cash_amounts.withdrawal_value,
            "Cash_Bal": today_cash_amounts.cash_value,
            "Ecash_Bal": "N/A",
            "difference": "N/A",
        })

    return comparing_table


@router.get("/cash/view/all/{society_id}")
async def get_cash_account_balance_society(society_id: int,
                                           user: dict = Depends(get_current_user),
                                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    current_date = datetime.now()
    today_date = current_date.strftime('%Y-%m-%d')

    comparing_table = []

    today_cash_amounts = db.query(models.CashAssociationAccount.date,
                                  models.CashAssociationAccount.id,
                                  models.CashAssociationAccount.cash_savings_bal,
                                  models.CashAssociationAccount.cash_loans_bal,
                                  models.CashAssociationAccount.cash_shares_bal,
                                  models.CashAssociationAccount.cash_value,
                                  models.CashAssociationAccount.transfers_value,
                                  models.CashAssociationAccount.withdrawal_value,
                                  models.Association.association_name
                                  ) \
        .join(models.Association,
              models.Association.association_id == models.CashAssociationAccount.association_id) \
        .join(models.AssociationType,
              models.AssociationType.associationtype_id == models.Association.association_type_id) \
        .join(models.Society,
              models.Society.id == models.AssociationType.society_id) \
        .filter(models.Society.id == society_id,
                models.CashAssociationAccount.date < today_date) \
        .all()

    today_ecash_amounts = db.query(models.MomoAccountAssociation.date,
                                   models.MomoAccountAssociation.id,
                                   models.MomoAccountAssociation.momo_bal,
                                   models.MomoAccountAssociation.status,
                                   models.MomoAccountAssociation.button,
                                   models.Association.association_name,
                                   ) \
        .select_from(models.MomoAccountAssociation) \
        .join(models.Association,
              models.Association.association_id == models.MomoAccountAssociation.association_id) \
        .join(models.AssociationType,
              models.AssociationType.associationtype_id == models.Association.association_type_id) \
        .join(models.Society,
              models.Society.id == models.AssociationType.society_id) \
        .filter(models.Society.id == society_id,
                models.MomoAccountAssociation.date < today_date) \
        .all()

    maa = aliased(models.MomoAccountAssociation)
    caa = aliased(models.CashAssociationAccount)

    result = db.query(
        maa.date.label('mdate'),
        # caa.date.label('cdate'),
        maa.momo_bal,
        caa.cash_value,
        caa.transfers_value,
        caa.withdrawal_value,
        maa.status,
        maa.id,
        # caa.id,
        # caa.association_id.label('cash_asso'),
        # maa.association_id.label('momo_asso'),
        models.Association.association_name,
        maa.button
    ).outerjoin(
        caa,
        ((maa.date == caa.date) & (maa.association_id == caa.association_id))
    ).join(
        models.Association, models.Association.association_id == maa.association_id
    ).join(
        models.AssociationType,
        models.AssociationType.associationtype_id == models.Association.association_type_id
    ).join(models.Society,
           models.Society.id == models.AssociationType.society_id
           ).filter(
        models.Society.id == society_id,
        maa.date != today_date
    ).all()

    return {"Data": result}


class Filterd(BaseModel):
    society_id: int
    fromm: str
    to: str


@router.post("/cash/view/filtered")
async def get_filterd_cash_account_balance_society(society: Filterd,
                                                   user: dict = Depends(get_current_user),
                                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    current_date = datetime.now()

    today_date = current_date.strftime('%Y-%m-%d')

    maa = aliased(models.MomoAccountAssociation)
    caa = aliased(models.CashAssociationAccount)

    result = db.query(
        maa.date.label('mdate'),
        # caa.date.label('cdate'),
        maa.momo_bal,
        caa.cash_value,
        caa.transfers_value,
        caa.withdrawal_value,
        maa.status,
        maa.id,
        # caa.id,
        # caa.association_id.label('cash_asso'),
        # maa.association_id.label('momo_asso'),
        models.Association.association_name,
        maa.button
    ).outerjoin(
        caa,
        ((maa.date == caa.date) & (maa.association_id == caa.association_id))
    ).join(
        models.Association, models.Association.association_id == maa.association_id
    ).join(
        models.AssociationType,
        models.AssociationType.associationtype_id == models.Association.association_type_id
    ).join(models.Society,
           models.Society.id == models.AssociationType.society_id
           ).filter(
        models.Society.id == society.society_id,
        maa.date != today_date,
        maa.date >= society.fromm,
        maa.date <= society.to
    ).all()

    return {"Data": result}


@router.get("/today/everything/{association_id}")
async def get_all_transactions_combined_today(association_id: int,
                                              user: dict = Depends(get_current_user),
                                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    current_date = datetime.now()
    start_of_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    today_date = current_date.strftime('%Y-%m-%d')

    todays_savings_accounts_transactions = db.query(models.Members.firstname,
                                                    models.MemberSavingsAccount.id,
                                                    models.Members.lastname,
                                                    models.Members.member_id,
                                                    models.TransactionType.transactiontype_name,
                                                    models.SavingsTransaction.amount,
                                                    models.AssociationMembers.association_members_id,
                                                    # models.SavingsTransaction.transactiontype_id,
                                                    models.SavingsTransaction.transaction_date,
                                                    models.SavingsAccount.account_name,
                                                    # models.SavingsTransaction.narration,
                                                    # models.Users.username,
                                                    ) \
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
                models.SavingsTransaction.transaction_date <= end_of_day,
                models.TransactionType.transactiontype_name == "Deposit",
                not_(models.SavingsTransaction.narration.like("%Transfered to%")),
                not_(models.SavingsTransaction.narration.like("%Received from%"))
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    todays_savings_accounts_withdrawals = db.query(models.Members.firstname,
                                                   models.MemberSavingsAccount.id,
                                                   models.Members.lastname,
                                                   models.Members.member_id,
                                                   models.TransactionType.transactiontype_name,
                                                   models.SavingsTransaction.amount,
                                                   models.AssociationMembers.association_members_id,
                                                   models.SavingsTransaction.transactiontype_id,
                                                   models.SavingsTransaction.transaction_date,
                                                   models.SavingsTransaction.narration,
                                                   models.SavingsTransaction.balance,
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
                models.SavingsTransaction.transaction_date <= end_of_day,
                models.TransactionType.transactiontype_name == "Withdraw",
                not_(models.SavingsTransaction.narration.like("%Transferred to%")),
                not_(models.SavingsTransaction.narration.like("%Received from%"))
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    todays_savings_accounts_transfers = db.query(models.Members.firstname,
                                                 models.MemberSavingsAccount.id,
                                                 models.Members.lastname,
                                                 models.Members.member_id,
                                                 models.TransactionType.transactiontype_name,
                                                 models.SavingsTransaction.amount,
                                                 models.SavingsTransaction.transactiontype_id,
                                                 models.SavingsTransaction.transaction_date,
                                                 models.SavingsTransaction.narration,
                                                 models.SavingsTransaction.balance,
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
                models.SavingsTransaction.transaction_date <= end_of_day,
                (models.SavingsTransaction.narration.like("%Transferred to:%")) |
                (models.SavingsTransaction.narration.like("%Received from:%"))
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    todays_loan_accounts_transactions = db.query(models.Members.firstname,
                                                 models.MemberLoanAccount.id,
                                                 models.Members.lastname,
                                                 models.Members.member_id,
                                                 models.TransactionType.transactiontype_name,
                                                 models.LoansTransaction.amount,
                                                 models.AssociationMembers.association_members_id,
                                                 models.LoansTransaction.transaction_date,
                                                 models.LoanAccount.account_name,
                                                 # models.LoansTransaction.narration,
                                                 # models.Users.username
                                                 ) \
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
                models.LoansTransaction.transactiontype_id == 1,
                models.LoansTransaction.transaction_date >= start_of_day,
                models.LoansTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .all()

    todays_share_accounts_transactions = db.query(models.Members.firstname,
                                                  models.MemberShareAccount.id,
                                                  models.Members.lastname,
                                                  models.Members.member_id,
                                                  models.TransactionType.transactiontype_name,
                                                  models.SharesTransaction.amount,
                                                  models.AssociationMembers.association_members_id,
                                                  models.SharesTransaction.transaction_date,
                                                  models.ShareAccount.account_name,
                                                  # models.SharesTransaction.narration,
                                                  # models.Users.username
                                                  ) \
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

    # today_transaction = union_all([todays_savings_accounts_transactions,
    #                                todays_share_accounts_transactions,
    #                                todays_loan_accounts_transactions])
    all_one = []
    for item in todays_savings_accounts_transactions:
        all_one.append(item)
    for item in todays_share_accounts_transactions:
        all_one.append(item)
    for item in todays_loan_accounts_transactions:
        all_one.append(item)

    # all_them = [todays_savings_accounts_transactions, todays_share_accounts_transactions,
    #             todays_loan_accounts_transactions]
    return {"All_One": all_one,
            "Withdrawals": todays_savings_accounts_withdrawals,
            "Transfers": todays_savings_accounts_transfers}
    # return todays_savings_accounts_transactions, todays_share_accounts_transactions, todays_loan_accounts_transactions


class Som(BaseModel):
    association_id: int
    date: str


@router.post("/today/everything")
async def get_all_transactions_combined(som: Som,
                                        user: dict = Depends(get_current_user),
                                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    # current_date = datetime.now()
    # start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    # end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    date_obj = datetime.strptime(som.date, "%Y-%m-%d")

    start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)

    todays_savings_accounts_transactions = db.query(models.Members.firstname,
                                                    models.MemberSavingsAccount.id,
                                                    models.Members.lastname,
                                                    models.Members.member_id,
                                                    models.TransactionType.transactiontype_name,
                                                    models.SavingsTransaction.amount,
                                                    models.AssociationMembers.association_members_id,
                                                    # models.SavingsTransaction.transactiontype_id,
                                                    models.SavingsTransaction.transaction_date,
                                                    models.SavingsAccount.account_name,
                                                    # models.SavingsTransaction.narration,
                                                    # models.Users.username,
                                                    ) \
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
        .filter(models.Association.association_id == som.association_id,
                models.SavingsTransaction.transaction_date >= start_of_day,
                models.SavingsTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .all()

    todays_loan_accounts_transactions = db.query(models.Members.firstname,
                                                 models.MemberLoanAccount.id,
                                                 models.Members.lastname,
                                                 models.Members.member_id,
                                                 models.TransactionType.transactiontype_name,
                                                 models.LoansTransaction.amount,
                                                 models.AssociationMembers.association_members_id,
                                                 models.LoansTransaction.transaction_date,
                                                 models.LoanAccount.account_name,
                                                 # models.LoansTransaction.narration,
                                                 # models.Users.username
                                                 ) \
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
        .filter(models.Association.association_id == som.association_id,
                models.LoansTransaction.transactiontype_id == 1,
                models.LoansTransaction.transaction_date >= end_of_day,
                models.LoansTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .all()

    todays_share_accounts_transactions = db.query(models.Members.firstname,
                                                  models.MemberShareAccount.id,
                                                  models.Members.lastname,
                                                  models.Members.member_id,
                                                  models.TransactionType.transactiontype_name,
                                                  models.SharesTransaction.amount,
                                                  models.AssociationMembers.association_members_id,
                                                  models.SharesTransaction.transaction_date,
                                                  models.ShareAccount.account_name,
                                                  # models.SharesTransaction.narration,
                                                  # models.Users.username
                                                  ) \
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
        .filter(models.Association.association_id == som.association_id,
                models.SharesTransaction.transaction_date >= start_of_day,
                models.SharesTransaction.transaction_date <= end_of_day
                ) \
        .order_by(desc(models.SharesTransaction.transaction_id)) \
        .all()

    # today_transaction = union_all([todays_savings_accounts_transactions,
    #                                todays_share_accounts_transactions,
    #                                todays_loan_accounts_transactions])
    all_one = []
    for item in todays_savings_accounts_transactions:
        all_one.append(item)
    for item in todays_share_accounts_transactions:
        all_one.append(item)
    for item in todays_loan_accounts_transactions:
        all_one.append(item)

    # all_them = [todays_savings_accounts_transactions, todays_share_accounts_transactions,
    #             todays_loan_accounts_transactions]
    return {"All_One": all_one}
    # return todays_savings_accounts_transactions, todays_share_accounts_transactions, todays_loan_accounts_transactions


@router.get("society/reconcile/{association_type_id}")
async def get_societies_association_balances_to_reconcile(association_type_id: int,
                                                          user: dict = Depends(get_current_user),
                                                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    set_them_all = db.query(models.Association).filter(
        models.Association.association_type_id == association_type_id).all()

    for item in set_them_all:
        set_cash_account_balances(association_id=item.association_id,
                                  user=user,
                                  db=db)

    comparing_table = []

    today_cash_amounts = db.query(models.CashAssociationAccount.date,
                                  models.CashAssociationAccount.id,
                                  models.CashAssociationAccount.cash_savings_bal,
                                  models.CashAssociationAccount.cash_loans_bal,
                                  models.CashAssociationAccount.cash_shares_bal,
                                  models.CashAssociationAccount.cash_value,
                                  models.Association.association_name
                                  ) \
        .select_from(models.AssociationType) \
        .join(models.Association,
              models.AssociationType.associationtype_id == models.Association.association_type_id) \
        .join(models.CashAssociationAccount,
              models.CashAssociationAccount.association_id == models.Association.association_id) \
        .filter(models.AssociationType.associationtype_id == association_type_id) \
        .order_by(desc(models.CashAssociationAccount.id)) \
        .all()

    today_ecash_amounts = db.query(models.MomoAccountAssociation.date,
                                   models.MomoAccountAssociation.id,
                                   models.MomoAccountAssociation.momo_bal,
                                   ) \
        .select_from(models.AssociationType) \
        .join(models.Association,
              models.AssociationType.associationtype_id == models.Association.association_type_id) \
        .join(models.MomoAccountAssociation,
              models.MomoAccountAssociation.association_id == models.Association.association_id) \
        .filter(models.AssociationType.associationtype_id == association_type_id) \
        .order_by(desc(models.MomoAccountAssociation.id)) \
        .all()

    if today_ecash_amounts:
        comparing_table.append({
            "Id": today_cash_amounts.id,
            "Association": today_cash_amounts.association_name,
            "Date": today_cash_amounts.date,
            "Cash_Bal": today_cash_amounts.cash_value,
            "Ecash_Bal": today_ecash_amounts.momo_bal,
            "difference": round(today_cash_amounts.cash_savings_bal - today_ecash_amounts.momo_bal, 2),
        })
    else:
        comparing_table.append({
            "Id": today_cash_amounts.id,
            "Date": today_cash_amounts.date,
            "Cash_Bal": today_cash_amounts.cash_value,
            "Ecash_Bal": "N/A",
            "difference": "N/A",
        })

    return comparing_table


@router.get("/transaction/sumary/{association_id}")
async def get_association_transaction_details(association_id: int,
                                              user: dict = Depends(get_current_user),
                                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_date = datetime.now()
    today_date = current_date.strftime('%Y-%m-%d')

    cash_amounts = db.query(models.CashAssociationAccount.date,
                            models.CashAssociationAccount.id,
                            models.CashAssociationAccount.cash_savings_bal,
                            models.CashAssociationAccount.cash_loans_bal,
                            models.CashAssociationAccount.cash_shares_bal,
                            models.CashAssociationAccount.cash_value
                            ) \
        .filter(models.CashAssociationAccount.association_id == association_id,
                models.CashAssociationAccount.date != today_date) \
        .order_by(desc(models.CashAssociationAccount.id)) \
        .all()

    Ecash_amounts = db.query(models.MomoAccountAssociation.date,
                             models.MomoAccountAssociation.id,
                             models.MomoAccountAssociation.momo_bal,
                             ) \
        .filter(models.MomoAccountAssociation.association_id == association_id,
                models.MomoAccountAssociation.date != today_date) \
        .order_by(desc(models.MomoAccountAssociation.id)) \
        .all()

    dtat = []

    for i, g in zip(cash_amounts, Ecash_amounts):
        if i.date == g.date:
            dtat.append({
                "id": i.id,
                "date": i.date,
                "cash_savings_bal": i.cash_savings_bal,
                "cash_loans_bal": i.cash_loans_bal,
                "cash_shares_bal": i.cash_shares_bal,
                "cash_value": i.cash_value,
                "momo_bal": g.momo_bal
            })

    return dtat


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
