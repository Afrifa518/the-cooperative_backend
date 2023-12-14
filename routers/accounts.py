import sys

from sqlalchemy import desc, func

sys.path.append("../..")

from typing import Optional, List
from fastapi import Depends, HTTPException, APIRouter, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, get_user_exception
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from datetime import datetime

router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class SavingsAccount(BaseModel):
    account_name: str
    is_refundable: bool
    medium_of_exchange: str
    interest_over_a_year: Optional[float]
    stamp_value: Optional[str]


class LoanAccount(BaseModel):
    id: Optional[int]
    account_name: str
    interest_amt: float
    application_fee: float
    proccessing_fee: float
    min_amt: float
    max_amt: float


class ShareAccount(BaseModel):
    account_name: str
    share_value: float
    interest_amt: float


class CommodityAccount(BaseModel):
    warehouse: str
    commodities: Optional[List[int]] = None
    community: str
    society_id: int
    rebagging_fee: float
    stacking_fee: float
    destoning_fee: float
    cleaning_fee: float
    storage_fee: float
    tax_fee: float
    stitching_fee: float
    loading_fee: float
    empty_sack_cost_fee: float


class SocietyAccounts(BaseModel):
    account_name: str
    society_id: int
    purpose: Optional[str]


@router.delete("/delete_acc/save/{savings_acc_id}")
async def delete_savings_account(savings_acc_id: int,
                                 user: dict = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    rjjb = db.query(models.MemberSavingsAccount).filter(models.MemberSavingsAccount.id == savings_acc_id).first()
    bob = rjjb
    if rjjb.current_balance < 0:
        return "Depts must be cleared before deleting account"
    elif rjjb.current_balance > 0:
        return "Account must be empty before deleting"
    else:
        tra = db.query(models.SavingsTransaction).filter(
            models.SavingsTransaction.savings_acc_id == savings_acc_id).delete(synchronize_session=False)

        db.commit()
        db.query(models.MemberSavingsAccount).filter(models.MemberSavingsAccount.id == savings_acc_id).delete()
        db.commit()
        return "Account Deleted"


@router.delete("/delete_acc/loan/{loan_acc_id}")
async def delete_loans_account(loan_acc_id: int,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    rjjb = db.query(models.MemberLoanAccount).filter(models.MemberLoanAccount.id == loan_acc_id).first()
    bob = rjjb
    if rjjb.current_balance < 0:
        return "Depts must be cleared before deleting account"
    elif rjjb.current_balance > 0:
        return "Account must be empty before deleting"
    else:
        tra = db.query(models.LoansTransaction).filter(
            models.LoansTransaction.loans_acc_id == loan_acc_id).delete(synchronize_session=False)

        db.commit()
        db.query(models.MemberLoanAccount).filter(models.MemberLoanAccount.id == loan_acc_id).delete()
        db.commit()
        return "Account Deleted"


@router.delete("/delete_acc/share/{share_acc_id}")
async def delete_loans_account(share_acc_id: int,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    rjjb = db.query(models.MemberShareAccount).filter(models.MemberShareAccount.id == share_acc_id).first()
    bob = rjjb
    if rjjb.current_balance < 0:
        return "Depts must be cleared before deleting account"
    elif rjjb.current_balance > 0:
        return "Account must be empty before deleting"
    else:
        tra = db.query(models.SharesTransaction).filter(
            models.SharesTransaction.shares_acc_id == share_acc_id).delete(synchronize_session=False)

        db.commit()
        db.query(models.MemberShareAccount).filter(models.MemberShareAccount.id == share_acc_id).delete()
        db.commit()
        return "Account Deleted"


@router.delete("/delete_acc/commodity/{commodity_acc_id}")
async def delete_loans_account(commodity_acc_id: int,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    rjjb = db.query(models.MemberCommodityAccount).filter(models.MemberCommodityAccount.id == commodity_acc_id).first()
    bob = rjjb
    if rjjb.cash_value < 0:
        return "Depts must be cleared before deleting account"
    elif rjjb.cash_value > 0:
        return "Account must be empty before deleting"
    else:
        tra = db.query(models.CommodityTransactions).filter(
            models.CommodityTransactions.commodity_acc_id == commodity_acc_id).delete(synchronize_session=False)

        db.commit()
        db.query(models.MemberCommodityAccount).filter(models.MemberCommodityAccount.id == commodity_acc_id).delete()
        db.commit()
        return "Account Deleted"


@router.post("/society/account")
async def create_society_account(account: SocietyAccounts,
                                 user: dict = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    date = datetime.now()
    openDate = date.strftime("%Y-%m-%d")

    fg = db.query(models.SocietyBankAccounts) \
        .filter(models.SocietyBankAccounts.account_name == account.account_name,
                models.SocietyBankAccounts.society_id == account.society_id) \
        .first()
    if fg:
        return "Account name already exists"
    accoun_model = models.SocietyBankAccounts()
    accoun_model.society_id = account.society_id
    accoun_model.account_name = account.account_name
    accoun_model.current_balance = 0.00
    accoun_model.open_date = openDate
    accoun_model.purpose = account.purpose
    accoun_model.opened_by = user.get("id")

    db.add(accoun_model)
    db.flush()
    db.commit()

    return "Account Opened"


@router.get("/society/all/{society_id}")
async def get_society(society_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_balance_total = 0
    dd = db.query(models.SocietyBankAccounts).filter(models.SocietyBankAccounts.society_id == society_id).all()
    name = db.query(models.Society).filter(models.Society.id == society_id).first()

    for item in dd:
        current_balance_total += item.current_balance

    return {"Accounts": dd, "Society_Name": name.society, "Total": current_balance_total}


@router.post("/payment/details")
async def payment_details(transaction_id: int = Form(...),
                          bank_id: int = Form(...),
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    dh = db.query(models.UserAccountTransactions,
                  models.Users,
                  models.UserRoles).join(models.UserAccount,
                                         models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id).join(
        models.Users,
        models.Users.id == models.UserAccount.user_id).join(models.UserRoles,
                                                            models.UserRoles.id == models.Users.role_id).filter(
        models.UserAccountTransactions.transaction_id == transaction_id).first()
    dc = db.query(models.SocietyBankAccounts).filter(models.SocietyBankAccounts.id == bank_id).first()

    current_bank_amount = dc.current_balance
    amount_after_disbursement = current_bank_amount - dh.UserAccountTransactions.amount
    bank_account_name = dc.account_name
    funds_reciever = dh.Users.firstName + " " + dh.Users.lastName
    reason_for_funds = dh.UserAccountTransactions.narration
    request_date = dh.UserAccountTransactions.request_date
    reciever_role = dh.UserRoles.role_name
    reciever_email = dh.Users.email

    return {
        "Bank_Account_Name": bank_account_name,
        "Funds_Reciever": funds_reciever,
        "Reason_For_Funds": reason_for_funds,
        "Request_Date": request_date,
        "Reciever_Role": reciever_role,
        "Reciever_Email": reciever_email,
        "Current_Bank_Amount": current_bank_amount,
        "Amount_After_Disbursement": amount_after_disbursement,
        "Amount_Requesting": dh.UserAccountTransactions.amount
    }


@router.post("/disburse/funds")
async def disbures_funds(transaction_id: int = Form(...),
                         bank_id: int = Form(...),
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    dh = (db.query(models.UserAccountTransactions,
                   models.Users,
                   models.UserRoles)
          .join(models.UserAccount,
                models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id)
          .join(models.Users, models.Users.id == models.UserAccount.user_id)
          .join(models.UserRoles, models.UserRoles.id == models.Users.role_id)
          .filter(models.UserAccountTransactions.transaction_id == transaction_id)
          .first())

    transaction = db.query(models.UserAccountTransactions) \
        .filter(models.UserAccountTransactions.transaction_id == transaction_id) \
        .first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    transaction.status = "Disbursed"
    transaction.disburse_date = datetime.now()
    db.commit()

    er = db.query(models.UserAccount).filter(models.UserAccount.user_id == dh.Users.id).first()
    er.current_balance = (er.current_balance + transaction.amount)
    db.commit()

    bank_account = db.query(models.SocietyBankAccounts).filter(models.SocietyBankAccounts.id == bank_id).first()
    bank_account.current_balance = (bank_account.current_balance - transaction.amount)
    db.commit()
    dj = models.SocietyTransactions(
        transactiontype_id=2,
        amount=transaction.amount,
        prep_by=user.get("id"),
        narration=f"Disbursed to {dh.Users.firstName} {dh.Users.lastName}",
        transaction_date=datetime.now(),
        balance=bank_account.current_balance - transaction.amount,
        society_account_id=bank_id
    )
    db.add(dj)
    db.commit()

    return "Funds Disbursed"


@router.get("/society/transfer/all/{society_acc_id}")
async def get_society_for_transfer(society_acc_id: int,
                                   user: dict = Depends(get_current_user),
                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    rr = db.query(models.SocietyBankAccounts).filter(models.SocietyBankAccounts.id != society_acc_id).all()

    return {"rr": rr}


@router.post("/savings")
async def create_savings(savings: SavingsAccount,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    account_model = models.SavingsAccount()
    account_model.account_name = savings.account_name
    account_model.is_refundable = savings.is_refundable
    account_model.medium_of_exchange = savings.medium_of_exchange
    account_model.interest_over_a_year = savings.interest_over_a_year
    account_model.stamp_value = savings.stamp_value

    db.add(account_model)
    db.flush()
    db.commit()

    return "Setup Complete"


class EditSavingsAccount(BaseModel):
    id: int
    account_name: str
    is_refundable: bool
    medium_of_exchange: str
    interest_over_a_year: Optional[float]
    stamp_value: Optional[int]


@router.post("/savings/edit")
async def edit_savings(savings: EditSavingsAccount,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    if savings.medium_of_exchange == "cash":
        update_data = {
            models.SavingsAccount.account_name: savings.account_name,
            models.SavingsAccount.is_refundable: savings.is_refundable,
            models.SavingsAccount.medium_of_exchange: savings.medium_of_exchange,
            models.SavingsAccount.interest_over_a_year: savings.interest_over_a_year,
            models.SavingsAccount.stamp_value: None
        }
    else:
        update_data = {
            models.SavingsAccount.account_name: savings.account_name,
            models.SavingsAccount.is_refundable: savings.is_refundable,
            models.SavingsAccount.medium_of_exchange: savings.medium_of_exchange,
            models.SavingsAccount.interest_over_a_year: savings.interest_over_a_year,
            models.SavingsAccount.stamp_value: savings.stamp_value
        }

    db.query(models.SavingsAccount).filter(models.SavingsAccount.id == savings.id).update(update_data)
    db.commit()

    return "Edit Complete"


class Transaction(BaseModel):
    transaction_type_id: int
    amount: float
    narration: Optional[str]


@router.post("/transact_funds")
async def transaction_funds(transaction_type_id: int = Form(...),
                            amount: int = Form(...),
                            narration: Optional[str] = Form(None),
                            user: dict = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    acc_id = db.query(models.UserAccount).filter(models.UserAccount.user_id == user.get("id")).first()
    if transaction_type_id == 1:
        req = models.UserAccountTransactions(
            transaction_type_id=transaction_type_id,
            amount=amount,
            user_account_id=acc_id.user_account_id,
            narration=narration,
            request_date=datetime.now(),
            disburse_date=None,
            status="Request",
            balance=acc_id.current_balance
        )
        db.add(req)
        db.commit()
    elif transaction_type_id == 2:
        if acc_id.current_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient Funds")
        else:
            acc_id.current_balance -= amount
            db.commit()
            req = models.UserAccountTransactions(
                transaction_type_id=transaction_type_id,
                amount=amount,
                user_account_id=acc_id.user_account_id,
                narration=narration,
                request_date=datetime.now(),
                disburse_date=datetime.now(),
                status="Withdrawal",
                balance=acc_id.current_balance
            )
            db.add(req)
            db.commit()
        db.add(req)
        db.commit()

    return "Funds Requested"


@router.post("/expense/list")
async def get_all_expense_list(which: Optional[str] = Form(None),
                               start_date: Optional[str] = Form(None),
                               end_date: Optional[str] = Form(None),
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    if which == "request":
        dh = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.request_date,
                      models.UserAccountTransactions.amount,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Request",
                    func.date(models.UserAccountTransactions.request_date) >= start_date,
                    func.date(models.UserAccountTransactions.request_date) <= end_date) \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()

        reg_sum_amount = 0
        reg_sum_balance = 0
        for amount in dh:
            reg_sum_amount += amount.amount
            reg_sum_balance += amount.balance
    else:
        dh = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.request_date,
                      models.UserAccountTransactions.amount,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Request") \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()

        reg_sum_amount = 0
        reg_sum_balance = 0
        for amount in dh:
            reg_sum_amount += amount.amount
            reg_sum_balance += amount.balance

    if which == 'approval':
        dg = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.request_date,
                      models.UserAccountTransactions.amount,
                      models.ApprovalMessage.message,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.ApprovalMessage,
                  models.ApprovalMessage.id == models.UserAccountTransactions.message_id) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Approved",
                    func.date(models.UserAccountTransactions.request_date) >= start_date,
                    func.date(models.UserAccountTransactions.request_date) <= end_date) \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()
        apr_sum_amount = 0
        apr_sum_balance = 0
        for amount in dg:
            apr_sum_amount += amount.amount
            apr_sum_balance += amount.balance

    else:
        dg = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.request_date,
                      models.UserAccountTransactions.amount,
                      models.ApprovalMessage.message,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.ApprovalMessage,
                  models.ApprovalMessage.id == models.UserAccountTransactions.message_id) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Approved") \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()
        apr_sum_amount = 0
        apr_sum_balance = 0
        for amount in dg:
            apr_sum_amount += amount.amount
            apr_sum_balance += amount.balance

    if which == 'reject':
        df = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.request_date,
                      models.ApprovalMessage.message,
                      models.UserAccountTransactions.amount,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.ApprovalMessage,
                  models.ApprovalMessage.id == models.UserAccountTransactions.message_id) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Rejected",
                    func.date(models.UserAccountTransactions.request_date) >= start_date,
                    func.date(models.UserAccountTransactions.request_date) <= end_date) \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()
        rej_sum_amount = 0
        rej_sum_balance = 0
        for amount in df:
            rej_sum_amount += amount.amount
            rej_sum_balance += amount.balance

    else:
        df = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.request_date,
                      models.ApprovalMessage.message,
                      models.UserAccountTransactions.amount,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.ApprovalMessage,
                  models.ApprovalMessage.id == models.UserAccountTransactions.message_id) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Rejected") \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()
        rej_sum_amount = 0
        rej_sum_balance = 0
        for amount in df:
            rej_sum_amount += amount.amount
            rej_sum_balance += amount.balance

    if which == 'disburse':
        dk = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.disburse_date,
                      models.ApprovalMessage.message,
                      models.UserAccountTransactions.amount,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.ApprovalMessage,
                  models.ApprovalMessage.id == models.UserAccountTransactions.message_id) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Disbursed",
                    func.date(models.UserAccountTransactions.request_date) >= start_date,
                    func.date(models.UserAccountTransactions.request_date) <= end_date) \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()
        dis_sum_amount = 0
        dis_sum_balance = 0
        for amount in dk:
            dis_sum_amount += amount.amount
            dis_sum_balance += amount.balance
    else:
        dk = db.query(models.UserAccountTransactions.transaction_id,
                      models.UserAccountTransactions.narration,
                      models.UserAccountTransactions.disburse_date,
                      models.ApprovalMessage.message,
                      models.UserAccountTransactions.amount,
                      models.UserAccountTransactions.status,
                      models.UserAccountTransactions.balance,
                      models.Users.firstName,
                      models.Users.lastName,
                      models.UserRoles.role_name) \
            .select_from(models.UserAccountTransactions) \
            .join(models.ApprovalMessage,
                  models.ApprovalMessage.id == models.UserAccountTransactions.message_id) \
            .join(models.TransactionType,
                  models.TransactionType.transactype_id == models.UserAccountTransactions.transaction_type_id) \
            .join(models.UserAccount,
                  models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
            .join(models.Users,
                  models.Users.id == models.UserAccount.user_id) \
            .join(models.UserRoles,
                  models.UserRoles.id == models.Users.role_id) \
            .filter(models.UserAccountTransactions.status == "Disbursed") \
            .order_by(desc(models.UserAccountTransactions.transaction_id)) \
            .all()
        dis_sum_amount = 0
        dis_sum_balance = 0
        for amount in dk:
            dis_sum_amount += amount.amount
            dis_sum_balance += amount.balance

    return {
        "Requested_Expenses": dh,
        "reg_amount_sum": reg_sum_amount,
        "reg_balance_sum": reg_sum_balance,
        "Approved_Expenses": dg,
        "apr_amount_sum": apr_sum_amount,
        "apr_balance_sum": apr_sum_balance,
        "Rejected_Expenses": df,
        "rej_amount_sum": rej_sum_amount,
        "rej_balance_sum": rej_sum_balance,
        "Disbursed_Expenses": dk,
        "dis_amount_sum": dis_sum_amount,
        "dis_balance_sum": dis_sum_balance,
    }


@router.post("/request/delete")
async def delete_request(transaction_id: int = Form(...),
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    dh = db.query(models.UserAccountTransactions) \
        .filter(models.UserAccountTransactions.transaction_id == transaction_id) \
        .delete()
    db.commit()
    return "Request Deleted"


@router.post("/request/approve")
async def approve_request(transaction_id: int = Form(...),
                          amount: int = Form(...),
                          actionMessage: str = Form(...),
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    dh = db.query(models.UserAccountTransactions) \
        .filter(models.UserAccountTransactions.transaction_id == transaction_id) \
        .first()
    if dh is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    if actionMessage:
        hh = f"{user.get('username')}: {actionMessage}"
        fr = models.ApprovalMessage(
            message=hh,
        )
        db.add(fr)
        db.commit()

        dh.status = "Approved"
        dh.amount = amount
        dh.message_id = fr.id
        db.commit()
    else:
        dh.status = "Approved"
        dh.amount = amount
        db.commit()

    return "Request Approved"


@router.post("/request/approve/use")
async def approve_request(transaction_id: int = Form(...),
                          amount: int = Form(...),
                          actionMessage: str = Form(...),
                          narration: str = Form(...),
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    dh = db.query(models.UserAccountTransactions) \
        .filter(models.UserAccountTransactions.transaction_id == transaction_id) \
        .first()
    if dh is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    if actionMessage:
        dh.narration = narration
        dh.amount = amount
        db.commit()
    else:
        dh.narration = narration
        dh.amount = amount
        db.commit()

    return "Request Approved"


@router.post("/request/disapprove")
async def disapprove_request(transaction_id: int = Form(...),
                             user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    dh = db.query(models.UserAccountTransactions) \
        .filter(models.UserAccountTransactions.transaction_id == transaction_id) \
        .first()
    if dh is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    dh.status = "Request"
    db.commit()
    return "Request Disapproved"


@router.post("/request/reject")
async def reject_request(transaction_id: int = Form(...),
                         amount: int = Form(...),
                         actionMessage: str = Form(...),
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    dh = db.query(models.UserAccountTransactions) \
        .filter(models.UserAccountTransactions.transaction_id == transaction_id) \
        .first()
    if dh is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    if actionMessage:
        hh = f"{user.get('username')}: {actionMessage}"
        fr = models.ApprovalMessage(
            message=hh,
        )
        db.add(fr)
        db.commit()

        dh.status = "Rejected"
        dh.amount = amount
        dh.message_id = fr.id
        db.commit()
    else:
        dh.status = "Rejected"
        dh.amount = amount
        db.commit()

    return "Request Rejected"


# @router.post("/setup")
# async def register_account(user: dict = Depends(get_current_user),
#                            db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     user_account = models.UserAccount()
#     user_account.user_id = user.get("id")
#     user_account.current_balance = 0.00
#
#     db.add(user_account)
#     db.commit()
#
#     return "Account Registered"


@router.get("/my_account")
async def get_my_account_details(user: dict = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    details = db.query(models.UserAccount).filter(models.UserAccount.user_id == user.get("id")).first()
    if details is None:
        user_account = models.UserAccount()
        user_account.user_id = user.get("id")
        user_account.current_balance = 0.00

        db.add(user_account)
        db.commit()
    transactions = db.query(models.UserAccountTransactions) \
        .join(models.UserAccount,
              models.UserAccount.user_account_id == models.UserAccountTransactions.user_account_id) \
        .filter(models.UserAccount.user_id == user.get("id")) \
        .order_by(desc(models.UserAccountTransactions.transaction_id)) \
        .all()
    return {"Details": details, "Transactions": transactions}


@router.get("/one/savings/{one_account_id}")
async def get_savings_info(one_account_id: int,
                           user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    de = db.query(models.SavingsAccount).filter(models.SavingsAccount.id == one_account_id).first()

    nu = db.query(models.MemberSavingsAccount).filter(models.MemberSavingsAccount.savings_id == one_account_id).all()

    return {
        "Account_Details": de,
        "Account_opened": nu,
    }


@router.get("/savings/details/{account_id}")
async def get_one_savings_account_details(account_id: int,
                                          user: dict = Depends(get_current_user),
                                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    rest = db.query(models.SavingsAccount).filter(models.SavingsAccount.id == account_id).first()

    return {"Account_Details": rest}


class MemberSavings(BaseModel):
    savings_id: int
    association_member_id: Optional[int]
    member_id: int


@router.post("/membersaving")
async def create_member_savings_account(acc: MemberSavings,
                                        user: dict = Depends(get_current_user),
                                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    member_account = models.MemberSavingsAccount()
    member_account.savings_id = acc.savings_id
    member_account.open_date = datetime.now()
    member_account.current_balance = 0.00
    member_account.association_member_id = acc.association_member_id
    member_account.member_id = acc.member_id

    db.add(member_account)
    db.commit()

    return "New Account Activated"


@router.get("/savings/")
async def get_savings(user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.SavingsAccount).all()


@router.post("/loan")
async def create_loan(loan: LoanAccount,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    namfwed = db.query(models.LoanAccount).all()

    if loan.id:
        loan_model = db.query(models.LoanAccount).filter(models.LoanAccount.id == loan.id).first()
        loan_model.account_name = loan.account_name
        loan_model.interest_amt = loan.interest_amt
        loan_model.application_fee = loan.application_fee
        loan_model.proccessing_fee = loan.proccessing_fee
        loan_model.min_amt = loan.min_amt
        loan_model.max_amt = loan.max_amt

        db.flush()
        db.commit()
        return "Changes done successfully"
    else:
        for ff in namfwed:
            if ff.account_name == loan.account_name:
                return "Loan Account Name Exists"
            else:
                loan_model = models.LoanAccount()
                loan_model.account_name = loan.account_name
                loan_model.interest_amt = loan.interest_amt
                loan_model.application_fee = loan.application_fee
                loan_model.proccessing_fee = loan.proccessing_fee
                loan_model.min_amt = loan.min_amt
                loan_model.max_amt = loan.max_amt
                db.add(loan_model)
                db.flush()
                db.commit()

                return "Setup Complete"


class MemberLoan(BaseModel):
    loan_id: int
    association_member_id: Optional[int]
    member_id: int


@router.post("/memberloan")
async def create_member_loan_account(acc: MemberLoan,
                                     user: dict = Depends(get_current_user),
                                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    member_account = models.MemberLoanAccount()
    member_account.loan_id = acc.loan_id
    member_account.open_date = datetime.now()
    member_account.current_balance = 0.00
    member_account.association_member_id = acc.association_member_id
    member_account.member_id = acc.member_id

    db.add(member_account)
    db.commit()

    return "New Account Activated"


@router.get("/loan/")
async def get_loans(user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.LoanAccount).all()


@router.post("/share")
async def create_share(share: ShareAccount,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    share_model = models.ShareAccount()
    share_model.account_name = share.account_name
    share_model.share_value = share.share_value
    share_model.interest_amt = share.interest_amt

    db.add(share_model)
    db.flush()
    db.commit()

    return "Setup Complete"


class MemberShare(BaseModel):
    share_id: int
    association_member_id: Optional[int]
    member_id: int


@router.post("/membershare")
async def create_member_loan_account(acc: MemberShare,
                                     user: dict = Depends(get_current_user),
                                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    member_account = models.MemberShareAccount()
    member_account.share_id = acc.share_id
    member_account.open_date = datetime.now()
    member_account.current_balance = 0.00
    member_account.association_member_id = acc.association_member_id
    member_account.member_id = acc.member_id

    db.add(member_account)
    db.commit()

    return "New Account Activated"


@router.get("/share/")
async def get_shares(user: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.ShareAccount).all()


@router.post("/commodity")
async def create_commodity(commodity: CommodityAccount,
                           user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    commodity_model = models.CommodityAccount()
    commodity_model.warehouse = commodity.warehouse
    commodity_model.community = commodity.community
    commodity_model.society_id = commodity.society_id
    commodity_model.rebagging_fee = commodity.rebagging_fee
    commodity_model.stacking_fee = commodity.stacking_fee
    commodity_model.destoning_fee = commodity.destoning_fee
    commodity_model.cleaning_fee = commodity.cleaning_fee
    commodity_model.storage_fee = commodity.storage_fee
    commodity_model.tax_fee = commodity.tax_fee
    commodity_model.stitching_fee = commodity.stitching_fee
    commodity_model.loading_fee = commodity.loading_fee
    commodity_model.empty_sack_cost_fee = commodity.empty_sack_cost_fee

    db.add(commodity_model)
    db.flush()
    db.commit()
    add_commodities(commodities=commodity.commodities, db=db)

    return "Warehouse Added"


@router.get("/commodities/{society_id}")
async def get_all_commodities_in_cluster(society_id: int,
                                         user: dict = Depends(get_current_user),
                                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    commodi = db.query(models.Commodities.id,
                       models.Commodities.commodity) \
        .select_from(models.SocietyCommodities) \
        .join(models.Commodities, models.Commodities.id == models.SocietyCommodities.commodities_id) \
        .join(models.Society,
              models.SocietyCommodities.society_id == models.Society.id) \
        .filter(models.Society.id == society_id) \
        .all()
    return {"All_Commodities": commodi}


@router.post("/commodities/joiner")
async def get_all_commodities_in_cluste_to_join_warehouser(society_id: int = Form(...),
                                                           com_acc_id: int = Form(...),
                                                           user: dict = Depends(get_current_user),
                                                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    exist = db.query(models.CommodityAccountCommodities).filter(
        models.CommodityAccountCommodities.commodity_account_id == com_acc_id).first()
    if exist:
        commodi = db.query(models.Commodities.id,
                           models.Commodities.commodity) \
            .select_from(models.SocietyCommodities) \
            .join(models.Commodities, models.Commodities.id == models.SocietyCommodities.commodities_id) \
            .filter(models.SocietyCommodities.society_id == society_id,
                    models.SocietyCommodities.commodities_id != exist.commodities_id) \
            .all()
    else:
        commodi = db.query(models.Commodities.id,
                           models.Commodities.commodity) \
            .select_from(models.SocietyCommodities) \
            .join(models.Commodities, models.Commodities.id == models.SocietyCommodities.commodities_id) \
            .filter(models.SocietyCommodities.society_id == society_id) \
            .all()
    return {"All_Commodities": commodi}


@router.post("/finally/add_com")
async def join_commodity_to_warehouse(warehouse_id: int = Form(...),
                                      commodity_id: int = Form(...),
                                      user: dict = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    fg = db.query(models.CommodityAccountCommodities).filter(
        models.CommodityAccountCommodities.commodity_account_id == warehouse_id,
        models.CommodityAccountCommodities.commodities_id == commodity_id).first()
    if fg is None:
        dh = models.CommodityAccountCommodities(
            commodities_id=commodity_id,
            commodity_account_id=warehouse_id
        )
        db.add(dh)
        db.commit()
        return "Commodity Added Successfully"
    else:
        return "Commodity Already Added"


def add_commodities(commodities: Optional[List[int]] = None,
                    db: Session = Depends(get_db)):
    commodity_account = db.query(models.CommodityAccount) \
        .order_by(desc(models.CommodityAccount.id)) \
        .first()

    if not commodity_account:
        raise HTTPException(status_code=404, detail="Commodity account not found")

    for commodity in commodities:
        commo_model = models.CommodityAccountCommodities(
            commodities_id=commodity,
            commodity_account_id=commodity_account.id
        )
        db.add(commo_model)
        db.commit()

    return "Successfully Created"


class MemberCommodity(BaseModel):
    commodity_id: int
    association_member_id: Optional[int]
    member_id: int


@router.post("/membercommodities")
async def create_member_commodity_account(acc: MemberCommodity,
                                          user: dict = Depends(get_current_user),
                                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    member_account = models.MemberCommodityAccount()
    member_account.commodity_id = acc.commodity_id
    member_account.open_date = datetime.now()
    member_account.cash_value = 0.00
    member_account.association_member_id = acc.association_member_id
    member_account.member_id = acc.member_id

    db.add(member_account)
    db.commit()

    return "New Account Activated"


class StoreCommodities(BaseModel):
    member_acc_id: int
    commodity_id: int
    grade: str
    units_id: int
    total_number: int
    rebagging_fee: bool
    stacking_fee: bool
    destoning_fee: bool
    cleaning_fee: bool
    storage_fee: bool
    tax_fee: bool
    stitching_fee: bool
    loading_fee: bool
    empty_sack_cost_fee: bool


#
# @router.post("/store/commodity")
# async def store_commodity(storage: StoreCommodities,
#                           user: dict = Depends(get_current_user),
#                           db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#
#     charges = db.query(models.CommodityAccount) \
#         .select_from(models.MemberCommodityAccount) \
#         .join(models.CommodityAccount,
#               models.CommodityAccount.id == models.MemberCommodityAccount.commodity_id) \
#         .filter(models.MemberCommodityAccount.id == storage.member_acc_id) \
#         .first()
#
#     price = db.query(models.CommodityGradeValues) \
#         .select_from(models.Commodities) \
#         .join(models.CommodityGradeValues,
#               models.Commodities.id == models.CommodityGradeValues.commodities_id) \
#         .filter(models.Commodities.id == storage.commodity_id,
#                 models.CommodityGradeValues.grade == storage.grade) \
#         .first()
#     unit = db.query(models.UnitsKg) \
#         .select_from(models.UnitsKg) \
#         .filter(models.UnitsKg.id == storage.units_id) \
#         .first()
#
#     weight = unit.unit_per_kg * storage.total_number
#     tons = weight / 1000
#
#     cash_value = 0
#     # add handling fee
#
#     modell = models.MemberCommodityAccCommodities(
#         member_acc_id=storage.member_acc_id,
#         commodities_id=storage.commodity_id,
#         units_id=storage.units_id,
#         total_number=storage.total_number,
#         commodity_cash_value=cash_value,
#         weight=weight,
#         tons=tons
#     )


@router.get("/commodity/{society_id}/")
async def get_commodities_warhouse(society_id: int,
                                   user: dict = Depends(get_current_user),
                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    warehouses = db.query(models.CommodityAccount.warehouse,
                          models.CommodityAccount.id,
                          models.CommodityAccount.society_id) \
        .select_from(models.CommodityAccount) \
        .filter(models.CommodityAccount.society_id == society_id) \
        .all()

    return {"Warehouse": warehouses}


@router.get("/commodities/warehouse/{member_acc_id}")
async def get_commodities(member_acc_id: int,
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    account = db.query(models.MemberCommodityAccount) \
        .filter(models.MemberCommodityAccount.id == member_acc_id) \
        .first()

    com = db.query(models.Commodities) \
        .select_from(models.CommodityAccountCommodities) \
        .join(models.Commodities,
              models.Commodities.id == models.CommodityAccountCommodities.commodities_id) \
        .filter(models.CommodityAccountCommodities.commodity_account_id == account.commodity_id) \
        .all()

    return {"Commodities": com}


@router.get("/commodities/charges/{member_acc_id}")
async def get_charges(member_acc_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    com = db.query(models.CommodityAccount) \
        .select_from(models.MemberCommodityAccount) \
        .join(models.CommodityAccount,
              models.CommodityAccount.id == models.MemberCommodityAccount.commodity_id) \
        .filter(models.MemberCommodityAccount.id == member_acc_id) \
        .all()

    return com


@router.get("/grade/values/{commodity_id}")
async def get_commodity_grade_values(commodity_id: int,
                                     user: dict = Depends(get_current_user),
                                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    grades = db.query(models.CommodityGradeValues) \
        .filter(models.CommodityGradeValues.commodities_id == commodity_id) \
        .all()

    unit_join = db.query(models.CommodityUnitsJoin) \
        .filter(models.CommodityUnitsJoin.commodity_id == commodity_id) \
        .all()
    units_kg = []
    for item in unit_join:
        extract = db.query(models.UnitsKg) \
            .filter(models.UnitsKg.id == item.unit_per_kg_id) \
            .first()
        units_kg.append(extract)

    return {"grades": grades, "units_kg": units_kg}


@router.get("/commodityty/all")
async def get_all_commodities_account(user: dict = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    warehouse = db.query(models.CommodityAccount.warehouse,
                         models.CommodityAccount.id,
                         models.CommodityAccount.community,
                         models.CommodityAccount.society_id) \
        .select_from(models.CommodityAccount) \
        .all()

    return {"Warehouse": warehouse}


@router.get("/commodityty/all/{association_memeber_id}")
async def get_all_commodities_account_in_soc(association_memeber_id: int,
                                             user: dict = Depends(get_current_user),
                                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    warehouse = db.query(models.CommodityAccount.warehouse,
                         models.CommodityAccount.id,
                         models.CommodityAccount.community,
                         models.CommodityAccount.society_id) \
        .select_from(models.AssociationMembers) \
        .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
        .join(models.AssociationType,
              models.Association.association_type_id == models.AssociationType.associationtype_id) \
        .join(models.Society, models.Society.id == models.AssociationType.society_id) \
        .join(models.CommodityAccount, models.CommodityAccount.society_id == models.Society.id) \
        .filter(models.AssociationMembers.association_members_id == association_memeber_id) \
        .all()

    return {"Warehouse": warehouse}


@router.get("/commodity/account/info/{warehouse_id}")
async def get_warehouse_infomation(warehouse_id: int,
                                   user: dict = Depends(get_current_user),
                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    basic_info = db.query(models.CommodityAccount.warehouse,
                          models.CommodityAccount.tax_fee,
                          models.CommodityAccount.storage_fee,
                          models.CommodityAccount.cleaning_fee,
                          models.CommodityAccount.destoning_fee,
                          models.CommodityAccount.stacking_fee,
                          models.CommodityAccount.rebagging_fee,
                          models.CommodityAccount.stitching_fee,
                          models.CommodityAccount.loading_fee,
                          models.CommodityAccount.empty_sack_cost_fee,
                          models.CommodityAccount.community,
                          ) \
        .select_from(models.CommodityAccount) \
        .filter(models.CommodityAccount.id == warehouse_id) \
        .first()

    related_commodities = db.query(models.Commodities) \
        .select_from(models.CommodityAccount) \
        .join(models.CommodityAccountCommodities,
              models.CommodityAccountCommodities.commodity_account_id == models.CommodityAccount.id) \
        .join(models.Commodities,
              models.CommodityAccountCommodities.commodities_id == models.Commodities.id) \
        .filter(models.CommodityAccount.id == warehouse_id) \
        .all()
    # print({"Basic_Info": basic_info, "Related Commodities": related_commodities})

    return {"Basic_Info": basic_info, "Related_Commodities": related_commodities}


@router.get("/account/{member_id}")
async def get_individual_member_accounts(member_id: int,
                                         user: dict = Depends(get_current_user),
                                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    all_savings_accounts = (
        db.query(
            models.MemberSavingsAccount.open_date,
            models.MemberSavingsAccount.id,
            models.MemberSavingsAccount.current_balance,
            models.SavingsAccount.account_name,
        )
        .select_from(models.MemberSavingsAccount)
        .join(models.SavingsAccount, models.MemberSavingsAccount.savings_id == models.SavingsAccount.id)
        .filter(models.MemberSavingsAccount.member_id == member_id)
        .all()
    )

    savings = []

    for row in all_savings_accounts:
        (

            open_date,
            id,
            current_balance,
            account_name,
        ) = row

        savings.append({
            "open_date": open_date,
            "ID": id,
            "Current_Balance": current_balance,
            "Account_Name": account_name,
        })

    all_loans_accounts = (
        db.query(
            models.MemberLoanAccount.current_balance,
            models.MemberLoanAccount.id,
            models.MemberLoanAccount.open_date,
            models.LoanAccount.account_name,
            models.LoanAccount.interest_amt
        )
        .select_from(models.MemberLoanAccount)
        .join(models.LoanAccount, models.MemberLoanAccount.loan_id == models.LoanAccount.id)
        .filter(models.MemberLoanAccount.member_id == member_id)
        .all()
    )
    loans = []
    for loanrow in all_loans_accounts:
        (
            current_balance,
            id,
            open_date,
            account_name,
            interest_amt,
        ) = loanrow

        loans.append({
            "current_balance": current_balance,
            "ID": id,
            "open_date": open_date,
            "account_name": account_name,
            "interest_amt": interest_amt,
        })

    shares = []
    all_shares_accounts = (
        db.query(
            models.MemberShareAccount.open_date,
            models.MemberShareAccount.id,
            models.MemberShareAccount.current_balance,
            models.ShareAccount.account_name,
            models.ShareAccount.share_value
        )
        .select_from(models.MemberShareAccount)
        .join(models.ShareAccount, models.MemberShareAccount.share_id == models.ShareAccount.id)
        .filter(models.MemberShareAccount.member_id == member_id)
        .all()
    )

    for sharerow in all_shares_accounts:
        (
            open_date,
            id,
            current_balance,
            account_name,
            share_value,
        ) = sharerow
        shares.append({
            "open_date": open_date,
            "ID": id,
            "current_balance": current_balance,
            "account_name": account_name,
            "share_value": share_value
        })

    commodity = []
    all_commodity_accounts = (
        db.query(
            models.MemberCommodityAccount.id,
            models.MemberCommodityAccount.open_date,
            models.MemberCommodityAccount.cash_value,
            models.CommodityAccount.warehouse,
        )
        .select_from(models.MemberCommodityAccount)
        .join(models.CommodityAccount, models.MemberCommodityAccount.commodity_id == models.CommodityAccount.id)
        .filter(models.MemberCommodityAccount.member_id == member_id)
        .all()
    )

    for commodityrow in all_commodity_accounts:
        (
            id,
            open_date,
            cash_value,
            warehouse,
        ) = commodityrow

        commodity.append({
            "ID": id,
            "open_date": open_date,
            "Amount_value": cash_value,
            "Warehouse_name": warehouse,
        })

    return {
        "Savings_acc": savings,
        "Loans_acc": loans,
        "Shares_acc": shares,
        "Commodity_acc": commodity
    }


@router.get("/accounts/{association_member_id}")
async def get_member_accounts(association_member_id: int,
                              user: dict = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    all_savings_accounts = (
        db.query(
            models.MemberSavingsAccount.open_date.label("msa_open_date"),
            models.MemberSavingsAccount.id.label("msa_id"),
            models.MemberSavingsAccount.current_balance.label("msa_current_balance"),
            models.SavingsAccount.account_name.label("sa_account_name"),
            models.SavingsAccount.id.label("sa_id")
        )
        .select_from(models.MemberSavingsAccount)
        .join(models.SavingsAccount, models.MemberSavingsAccount.savings_id == models.SavingsAccount.id)
        .filter(models.MemberSavingsAccount.association_member_id == association_member_id)
        .all()
    )

    savings = []

    for row in all_savings_accounts:
        (

            open_date,
            msa_id,
            current_balance,
            account_name,
            sa_id
        ) = row

        savings.append({
            "open_date": open_date,
            "ID": msa_id,
            "Current_Balance": current_balance,
            "Account_Name": account_name,
            "savings_id": sa_id,
        })

    all_loans_accounts = (
        db.query(
            models.MemberLoanAccount.current_balance.label("m_open_date"),
            models.MemberLoanAccount.id.label("m_id"),
            models.MemberLoanAccount.open_date.label("m_current_balance"),
            models.LoanAccount.account_name.label("loan_account_name"),
            models.LoanAccount.interest_amt.label("interest_amt"),
            models.LoanAccount.id.label("loan_id"),
        )
        .select_from(models.MemberLoanAccount)
        .join(models.LoanAccount, models.MemberLoanAccount.loan_id == models.LoanAccount.id)
        .filter(models.MemberLoanAccount.association_member_id == association_member_id)
        .all()
    )
    loans = []
    for loanrow in all_loans_accounts:
        (
            current_balance,
            m_id,
            open_date,
            account_name,
            interest_amt,
            loan_id
        ) = loanrow

        loans.append({
            "current_balance": current_balance,
            "ID": m_id,
            "open_date": open_date,
            "account_name": account_name,
            "interest_amt": interest_amt,
            "loan_id": loan_id
        })

    shares = []
    all_shares_accounts = (
        db.query(
            models.MemberShareAccount.open_date.label("msh_open_date"),
            models.MemberShareAccount.id.label("msh_id"),
            models.MemberShareAccount.current_balance.label("msh_current_balance"),
            models.ShareAccount.account_name.label("share_account_name"),
            models.ShareAccount.share_value.label("share_value"),
            models.ShareAccount.id.label("share_id")
        )
        .select_from(models.MemberShareAccount)
        .join(models.ShareAccount, models.MemberShareAccount.share_id == models.ShareAccount.id)
        .filter(models.MemberShareAccount.association_member_id == association_member_id)
        .all()
    )

    for sharerow in all_shares_accounts:
        (
            open_date,
            msh_id,
            current_balance,
            account_name,
            share_value,
            share_id
        ) = sharerow
        shares.append({
            "open_date": open_date,
            "ID": msh_id,
            "current_balance": current_balance,
            "account_name": account_name,
            "share_value": share_value,
            "share_id": share_id
        })

    commodity = []
    all_commodity_accounts = (
        db.query(
            models.MemberCommodityAccount.id.label("mca_id"),
            models.MemberCommodityAccount.open_date.label("mca_open_date"),
            models.MemberCommodityAccount.cash_value.label("mca_cash_value"),
            models.CommodityAccount.warehouse.label("ca_warehouse"),
            models.CommodityAccount.id.label("ca_id")
        )
        .select_from(models.MemberCommodityAccount)
        .join(models.CommodityAccount, models.MemberCommodityAccount.commodity_id == models.CommodityAccount.id)
        .filter(models.MemberCommodityAccount.association_member_id == association_member_id)
        .all()
    )

    for commodityrow in all_commodity_accounts:
        (
            mca_id,
            open_date,
            cash_value,
            warehouse,
            ca_id
        ) = commodityrow

        commodity.append({
            "ID": mca_id,
            "open_date": open_date,
            "Amount_value": cash_value,
            "Warehouse_name": warehouse,
            "commodity_id": ca_id
        })

    return {
        "Savings_acc": savings,
        "Loans_acc": loans,
        "Shares_acc": shares,
        "Commodity_acc": commodity
    }


@router.get("/save/{savings_account_id}")
async def get_account_info(savings_account_id: int,
                           user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    data_nkoa = (
        db.query(
            models.MemberSavingsAccount.id,
            models.MemberSavingsAccount.open_date,
            models.MemberSavingsAccount.current_balance
        ).filter(models.MemberSavingsAccount.id == savings_account_id).first()
    )
    timestamp = f"{data_nkoa.open_date}"
    datetime_obj = datetime.fromisoformat(timestamp)
    formatted_date = datetime_obj.strftime("%Y-%m-%d %H-%M-%S")
    data_nkoa_json = [
        {
            "id": data_nkoa.id,
            "open_date": formatted_date,
            "current_balance": data_nkoa.current_balance,
        }
    ]

    if not data_nkoa_json:
        return {}

    return data_nkoa_json


@router.get("/loan/{loans_account_id}")
async def get_loan_info(loans_account_id: int,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    data_nkoa = (
        db.query(
            models.MemberLoanAccount.id,
            models.MemberLoanAccount.open_date,
            models.MemberLoanAccount.current_balance,
            models.LoanAccount.min_amt,
            models.LoanAccount.max_amt
        ).select_from(models.MemberLoanAccount)
        .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id)
        .filter(models.MemberLoanAccount.id == loans_account_id).first()
    )
    timestamp = f"{data_nkoa.open_date}"
    datetime_obj = datetime.fromisoformat(timestamp)
    formatted_date = datetime_obj.strftime("%Y-%m-%d %H-%M-%S")
    data_nkoa_json = [
        {
            "id": data_nkoa.id,
            "open_date": formatted_date,
            "current_balance": data_nkoa.current_balance,
            "Min_amt": data_nkoa.min_amt,
            "Max_amt": data_nkoa.max_amt
        }
    ]

    if not data_nkoa_json:
        return {}

    return data_nkoa_json


@router.get("/share/{share_account_id}")
async def get_loan_info(share_account_id: int,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    data_nkoa = (
        db.query(
            models.MemberShareAccount.id,
            models.MemberShareAccount.open_date,
            models.MemberShareAccount.current_balance
        ).filter(models.MemberShareAccount.id == share_account_id).first()
    )
    timestamp = f"{data_nkoa.open_date}"
    datetime_obj = datetime.fromisoformat(timestamp)
    formatted_date = datetime_obj.strftime("%Y-%m-%d %H-%M-%S")
    data_nkoa_json = [
        {
            "id": data_nkoa.id,
            "open_date": formatted_date,
            "current_balance": data_nkoa.current_balance,
        }
    ]

    if not data_nkoa_json:
        return {}

    return data_nkoa_json


@router.get("/commodity/{commodity_account_id}")
async def get_commodity_info(commodity_account_id: int,
                             user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    data_nkoa = (
        db.query(
            models.MemberCommodityAccount.id,
            models.MemberCommodityAccount.open_date,
            models.MemberCommodityAccount.cash_value,
        ).filter(models.MemberCommodityAccount.id == commodity_account_id).first()
    )
    timestamp = f"{data_nkoa.open_date}"
    datetime_obj = datetime.fromisoformat(timestamp)
    formatted_date = datetime_obj.strftime("%Y-%m-%d %H-%M-%S")
    data_nkoa_json = [
        {
            "id": data_nkoa.id,
            "open_date": formatted_date,
            "amount_valued": data_nkoa.cash_value
        }
    ]

    if not data_nkoa_json:
        return {}

    return data_nkoa_json


@router.post("/process/storage")
async def process_storage(commodity_id: int = Form(...),
                          grade_id: int = Form(...),
                          unit_id: int = Form(...),
                          amount_storing: int = Form(...),
                          member_com_acc: int = Form(...),
                          rebag: bool = Form(...),
                          stack: bool = Form(...),
                          clean: bool = Form(...),
                          destone: bool = Form(...),
                          store: bool = Form(...),
                          stitch: bool = Form(...),
                          load: bool = Form(...),
                          empty_sack: bool = Form(...),
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    # UnitKg details
    unit = db.query(models.UnitsKg) \
        .filter(models.UnitsKg.id == unit_id).first()
    # Grade & Price details
    details = db.query(models.CommodityGradeValues) \
        .filter(models.CommodityGradeValues.id == grade_id).first()
    # Commodity details
    commodity = db.query(models.Commodities) \
        .filter(models.Commodities.id == commodity_id).first()
    # Charges & warehouse details
    charges = db.query(models.CommodityAccount) \
        .select_from(models.MemberCommodityAccount) \
        .join(models.CommodityAccount,
              models.CommodityAccount.id == models.MemberCommodityAccount.commodity_id) \
        .filter(models.MemberCommodityAccount.id == member_com_acc) \
        .first()

    weight = unit.unit_per_kg * amount_storing
    tons = f"{weight / 1000} tonnes" if weight > 1000 else f"Less than a ton"
    original_price_per_bg = unit.unit_per_kg * details.price_per_kg
    price_per_bg = 0
    # Rebagging
    if rebag:
        price_per_bg = original_price_per_bg - charges.rebagging_fee
    else:
        price_per_bg = original_price_per_bg
    # Stacking
    if stack:
        price_per_bg = price_per_bg - charges.stacking_fee
    else:
        price_per_bg = price_per_bg
    # Destoning
    if destone:
        price_per_bg = price_per_bg - charges.destoning_fee
    else:
        price_per_bg = price_per_bg
    # Cleaning
    if clean:
        price_per_bg = price_per_bg - charges.cleaning_fee
    else:
        price_per_bg = price_per_bg
    # Storage
    if store:
        price_per_bg = price_per_bg - charges.storage_fee
    else:
        price_per_bg = price_per_bg
    # Stitching
    if stitch:
        price_per_bg = price_per_bg - charges.stitching_fee
    else:
        price_per_bg = price_per_bg
    # Loading
    if load:
        price_per_bg = price_per_bg - charges.loading_fee
    else:
        price_per_bg = price_per_bg
    # Empty sack
    if empty_sack:
        price_per_bg = price_per_bg - charges.empty_sack_cost_fee
    else:
        price_per_bg = price_per_bg
    # Tax
    price_per_bg = price_per_bg - charges.tax_fee

    total_price_value = price_per_bg * amount_storing

    return {
        "Commodity": commodity.commodity,
        "Grade": details.grade,
        "Current_commodity_price": details.price_per_kg,
        "Unit_kg": unit.unit_per_kg,
        "Amount_storing": amount_storing,
        "Weight": weight,
        "Tons": tons,
        "Price_per_bag": original_price_per_bg,
        "charged_price_per_bg": price_per_bg,
        "total_cash_value": total_price_value
    }


@router.post("/store/commodity/original")
async def store_commodity(transaction_date: str = Form(...),
                          commodity_acc_id: int = Form(...),
                          number_of_commodities: int = Form(...),
                          commodities_id: int = Form(...),
                          cash_value: float = Form(...),
                          transaction_type_id: int = Form(...),
                          grade_id: int = Form(...),
                          units_id: int = Form(...),
                          weigth: int = Form(...),
                          tons: str = Form(...),
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    # get memeber account
    member_account = db.query(models.MemberCommodityAccount) \
        .filter(models.MemberCommodityAccount.id == commodity_acc_id) \
        .first()

    # save activity as transaction
    if transaction_type_id == 1:
        dbos = models.CommodityTransactions(
            prep_by=user.get("id"),
            narration="",
            transaction_date=transaction_date,
            commodity_acc_id=commodity_acc_id,
            amount_of_commodity=number_of_commodities,
            commodities_id=commodities_id,
            cash_value=cash_value,
            transaction_type_id=transaction_type_id,
            grade_id=grade_id,
            units_id=units_id,
            total_cash_balance=member_account.cash_value + cash_value if member_account.cash_value else cash_value
        )
        member_account.cash_value += cash_value
        db.add(dbos)
        db.commit()
    elif transaction_type_id == 2:
        dbos = models.CommodityTransactions(
            prep_by=user.get("id"),
            narration="",
            transaction_date=transaction_date,
            commodity_acc_id=commodity_acc_id,
            amount_of_commodity=number_of_commodities,
            commodities_id=commodities_id,
            cash_value=cash_value,
            transaction_type_id=transaction_type_id,
            grade_id=grade_id,
            units_id=units_id,
            total_cash_balance=member_account.cash_value - cash_value if member_account.cash_value else -cash_value
        )
        member_account.cash_value -= cash_value
        db.add(dbos)
        db.commit()

    # get commodities of the account
    already = db.query(models.MemberCommodityAccCommodities).filter(
        models.MemberCommodityAccCommodities.commodities_id == commodities_id,
        models.MemberCommodityAccCommodities.member_acc_id == commodity_acc_id).first()

    # get units
    real_units = db.query(models.UnitsKg).filter(models.UnitsKg.id == units_id).first()
    # get grades
    real_grades = db.query(models.CommodityGradeValues).filter(models.CommodityGradeValues.id == grade_id).first()
    # save or modify account's commodity
    if already:
        already.total_number += number_of_commodities
        already.commodity_cash_value += cash_value
        already.weight += weigth
        already.tons = f"{already.tons}, {tons}"
        already.units_id = f"{already.units_id}, {real_units.unit_per_kg}" if already.units_id != real_units.unit_per_kg else f"{already.units_id}"
        already.grades = f"{already.grades}, {real_grades.grade}" if already.grades != real_grades.grade else f"{already.grades}"

        db.commit()

        return "Commodity Stored Successfully"
    else:
        store_com_to_house = models.MemberCommodityAccCommodities(
            member_acc_id=commodity_acc_id,
            commodities_id=commodities_id,
            units_id=f"{real_units.unit_per_kg}",
            total_number=number_of_commodities,
            commodity_cash_value=cash_value,
            weight=weigth,
            tons=tons,
            grades=f"{real_grades.grade}",
        )
        db.add(store_com_to_house)
        db.commit()

        return "Commodity Stored Successfully"


@router.get("/com/transaction/details/{member_commodity_account_id}")
async def get_transaction_details(member_commodity_account_id: int,
                                  user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    commodities = []
    raw_commodities = db.query(models.Commodities,
                               models.MemberCommodityAccCommodities) \
        .select_from(models.MemberCommodityAccCommodities) \
        .join(models.Commodities, models.Commodities.id == models.MemberCommodityAccCommodities.commodities_id) \
        .filter(models.MemberCommodityAccCommodities.member_acc_id == member_commodity_account_id) \
        .all()

    for item in raw_commodities:
        data = {
            "id": item.Commodities.id,
            "commodity": item.Commodities.commodity,
            "units": item.MemberCommodityAccCommodities.units_id,
            "total_number": item.MemberCommodityAccCommodities.total_number,
            "commodity_cash_value": item.MemberCommodityAccCommodities.commodity_cash_value,
            "total_weight": item.MemberCommodityAccCommodities.weight,
            "tonnes": item.MemberCommodityAccCommodities.tons,
            "grade": item.MemberCommodityAccCommodities.grades
        }
        commodities.append(data)

    return {"Commodities": commodities}


@router.get("/current/prices/{commodity_id}")
async def get_all_commodity_prices(commodity_id: int,
                                   user: dict = Depends(get_current_user),
                                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    price = db.query(models.CommodityGradeValues) \
        .filter(models.CommodityGradeValues.commodities_id == commodity_id) \
        .all()
    return {"price": price}


@router.post("/my/activities/commodity")
async def my_activities_commodity(member_com_acc_id: int = Form(...),
                                  commodity_id: int = Form(...),
                                  start_date: Optional[str] = Form(None),
                                  end_date: Optional[str] = Form(None),
                                  user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    total_cash_value = 0
    total_bags = 0
    total_balance = 0

    if start_date and end_date:
        acts = db.query(models.CommodityTransactions.transaction_id,
                        models.Users.username,
                        models.CommodityTransactions.transaction_date,
                        models.CommodityTransactions.amount_of_commodity,
                        models.CommodityTransactions.commodities_id,
                        models.Commodities.commodity,
                        models.CommodityTransactions.cash_value,
                        models.CommodityTransactions.transaction_type_id,
                        models.CommodityGradeValues.grade,
                        models.UnitsKg.unit_per_kg,
                        models.CommodityTransactions.total_cash_balance) \
            .select_from(models.CommodityTransactions) \
            .join(models.Users, models.Users.id == models.CommodityTransactions.prep_by) \
            .join(models.CommodityGradeValues, models.CommodityGradeValues.id == models.CommodityTransactions.grade_id) \
            .join(models.UnitsKg, models.UnitsKg.id == models.CommodityTransactions.units_id) \
            .join(models.Commodities, models.Commodities.id == models.CommodityTransactions.commodities_id) \
            .filter(models.CommodityTransactions.commodity_acc_id == member_com_acc_id,
                    models.CommodityTransactions.commodities_id == commodity_id,
                    func.date(models.CommodityTransactions.transaction_date).between(start_date, end_date)) \
            .all()
        for item in acts:
            total_cash_value += item.cash_value if item.transaction_type_id == 1 else -item.cash_value
            total_bags += item.amount_of_commodity if item.transaction_type_id == 1 else -item.amount_of_commodity
            total_balance += item.total_cash_balance if item.transaction_type_id == 1 else -item.total_cash_balance
    else:
        acts = db.query(models.CommodityTransactions.transaction_id,
                        models.Users.username,
                        models.CommodityTransactions.transaction_date,
                        models.CommodityTransactions.amount_of_commodity,
                        models.CommodityTransactions.commodities_id,
                        models.Commodities.commodity,
                        models.CommodityTransactions.cash_value,
                        models.CommodityTransactions.transaction_type_id,
                        models.CommodityGradeValues.grade,
                        models.UnitsKg.unit_per_kg,
                        models.CommodityTransactions.total_cash_balance) \
            .select_from(models.CommodityTransactions) \
            .join(models.Users, models.Users.id == models.CommodityTransactions.prep_by) \
            .join(models.CommodityGradeValues, models.CommodityGradeValues.id == models.CommodityTransactions.grade_id) \
            .join(models.UnitsKg, models.UnitsKg.id == models.CommodityTransactions.units_id) \
            .join(models.Commodities, models.Commodities.id == models.CommodityTransactions.commodities_id) \
            .filter(models.CommodityTransactions.commodity_acc_id == member_com_acc_id,
                    models.CommodityTransactions.commodities_id == commodity_id) \
            .all()
        for item in acts:
            total_cash_value += item.cash_value if item.transaction_type_id == 1 else -item.cash_value
            total_bags += item.amount_of_commodity if item.transaction_type_id == 1 else -item.amount_of_commodity
            total_balance += item.total_cash_balance if item.transaction_type_id == 1 else -item.total_cash_balance

    return {
        "activities": acts,
        "total_cash_value": total_cash_value,
        "total_bags": total_bags,
        "total_balance": total_balance
    }


@router.delete("/movetotrash/{transaction_id}")
async def move_activity_to_trash(transaction_id: int,
                                 user: dict = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    before = db.query(models.CommodityTransactions).filter(
        models.CommodityTransactions.transaction_id == transaction_id).first()
    now = models.ActivityTrash(
        transaction_id=before.transaction_id,
        prep_by=before.prep_by,
        narration=before.narration,
        transaction_date=before.transaction_date,
        commodity_acc_id=before.commodity_acc_id,
        amount_of_commodity=before.amount_of_commodity,
        commodities_id=before.commodities_id,
        cash_value=before.cash_value,
        transaction_type_id=before.transaction_type_id,
        grade_id=before.grade_id,
        units_id=before.units_id,
        total_cash_balance=before.total_cash_balance
    )
    db.add(now)
    db.commit()
    after = db.query(models.CommodityTransactions).filter(
        models.CommodityTransactions.transaction_id == transaction_id).delete()
    db.commit()

    return "Activity deleted successfully"
