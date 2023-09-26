import sys

from sqlalchemy import desc, func

sys.path.append("../..")

from typing import Optional, List
from fastapi import Depends, HTTPException, APIRouter, status
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, get_user_exception
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from datetime import datetime

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class SavingsTransaction(BaseModel):
    transactiontype_id: int
    Amount: float
    narration: Optional[str]
    savings_acc_id: int


class SavingTransaction(BaseModel):
    transactiontype_idd: int
    Amountt: float
    narrationn: Optional[str]
    savings_acc_idd: int


class LoansTransaction(BaseModel):
    transactiontype_id: int
    Amount: float
    narration: Optional[str]
    loans_acc_id: int


class SharesTransaction(BaseModel):
    transactiontype_id: int
    Amount: float
    narration: Optional[str]
    shares_acc_id: int


# Savings

@router.post("/transaction/savings")
async def create_transactions_savings_acc(transactSave: SavingsTransaction,
                                          user: dict = Depends(get_current_user),
                                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    results = await check_for_stamps_and_cash(member_savings_acc=transactSave.savings_acc_id, user=user, db=db)

    if results.stamp_value:
        stamp = transactSave.Amount * results.stamp_value
        transactions_models = models.SavingsTransaction()
        transactions_models.transactiontype_id = transactSave.transactiontype_id
        transactions_models.amount = stamp
        transactions_models.prep_by = user.get("id")
        transactions_models.narration = transactSave.narration
        transactions_models.savings_acc_id = transactSave.savings_acc_id
        transactions_models.transaction_date = datetime.now()
    else:
        transactions_models = models.SavingsTransaction()
        transactions_models.transactiontype_id = transactSave.transactiontype_id
        transactions_models.amount = transactSave.Amount
        transactions_models.prep_by = user.get("id")
        transactions_models.narration = transactSave.narration
        transactions_models.savings_acc_id = transactSave.savings_acc_id
        transactions_models.transaction_date = datetime.now()

    db.add(transactions_models)
    db.flush()
    db.commit()

    return "Transaction Complete"


@router.post("/transaction/withdraw")
async def create_transactions_withdrawals_savings_acc(transactSavee: SavingTransaction,
                                                      user: dict = Depends(get_current_user),
                                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    transactions_models = models.SavingsTransaction()
    transactions_models.transactiontype_id = transactSavee.transactiontype_idd
    transactions_models.amount = transactSavee.Amountt
    transactions_models.prep_by = user.get("id")
    transactions_models.narration = transactSavee.narrationn
    transactions_models.savings_acc_id = transactSavee.savings_acc_idd
    transactions_models.transaction_date = datetime.now()

    db.add(transactions_models)
    db.flush()
    db.commit()

    return "Withdraw Successful"


# @router.get("/transactions/save/")
# async def get_savings_acc_transactions(user: dict = Depends(get_current_user),
#                                        db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     return db.query(models.SavingsTransaction).all()

@router.get("/sform/{member_savings_acc}")
async def check_for_stamps_and_cash(member_savings_acc: int,
                                    user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    stampOrCash = db.query(models.SavingsAccount.stamp_value) \
        .select_from(models.MemberSavingsAccount) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .filter(models.MemberSavingsAccount.id == member_savings_acc) \
        .first()
    if stampOrCash == None:
        return "Using Cash"
    else:
        dta = stampOrCash
        return dta
    # return stampOrCash


@router.get("/transaction/{member_savings_acc_id}")
async def get_one_savings_accounts_transactions(member_savings_acc_id: int,
                                                user: dict = Depends(get_current_user),
                                                db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    accounts_transaction = db.query(
        models.SavingsTransaction.transaction_date,
        models.SavingsTransaction.narration,
        models.Users.username,
        models.SavingsTransaction.amount,
        models.TransactionType.transactiontype_name,
        models.SavingsTransaction.transaction_id,
    ).select_from(models.SavingsTransaction) \
        .join(models.TransactionType,
              models.SavingsTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users,
              models.Users.id == models.SavingsTransaction.prep_by) \
        .filter(models.SavingsTransaction.savings_acc_id == member_savings_acc_id) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .group_by(
        models.SavingsTransaction.transaction_date,
        models.SavingsTransaction.narration,
        models.Users.username,
        models.SavingsTransaction.amount,
        models.TransactionType.transactiontype_name,
        models.SavingsTransaction.transaction_id,
    ) \
        .all()

    return accounts_transaction


# Loans

@router.post("/transaction/loans")
async def create_transactions_loans_request_acc(transactLoan: LoansTransaction,
                                                user: dict = Depends(get_current_user),
                                                db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    transactions_models = models.LoansTransaction()
    transactions_models.transactiontype_id = transactLoan.transactiontype_id
    transactions_models.amount = transactLoan.Amount
    transactions_models.prep_by = user.get("id")
    transactions_models.narration = transactLoan.narration
    transactions_models.loans_acc_id = transactLoan.loans_acc_id
    transactions_models.transaction_date = datetime.now()
    if transactLoan.transactiontype_id == 2:
        transactions_models.status = "Requested"
    elif transactLoan.transactiontype_id == 1:
        transactions_models.status = "Pay off"
    else:
        transactions_models.status = "N/A"

    db.add(transactions_models)
    db.flush()
    db.commit()

    if transactLoan.transactiontype_id == 2:
        return "Loan Requested"
    elif transactLoan.transactiontype_id == 1:
        return "Payment Successful"
    else:
        return "Transaction Complete"


@router.patch("/approve/loan/{transaction_id}")
async def approve_loan(transaction_id: int,
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .update({models.LoansTransaction.status: 'Approved'})

    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.commit()

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    return "Loan Approved"


@router.patch("/disburse/loan/{transaction_id}")
async def disburse_loan(transaction_id: int,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .update({models.LoansTransaction.status: 'Disbursed'})

    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.commit()

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    return "Loan Disbursed"


@router.get("/transaction/loan/{member_loans_acc_id}")
async def get_one_loan_accounts_transactions(member_loans_acc_id: int,
                                             user: dict = Depends(get_current_user),
                                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    accounts_transaction = db.query(
        models.LoansTransaction.transaction_date,
        models.LoansTransaction.narration,
        models.Users.username,
        models.LoansTransaction.amount,
        models.TransactionType.transactiontype_name,
        models.LoansTransaction.transaction_id,
        models.LoansTransaction.status
    ).select_from(models.LoansTransaction) \
        .join(models.TransactionType,
              models.LoansTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users,
              models.Users.id == models.LoansTransaction.prep_by) \
        .filter(models.LoansTransaction.loans_acc_id == member_loans_acc_id) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .group_by(
        models.LoansTransaction.transaction_date,
        models.LoansTransaction.narration,
        models.Users.username,
        models.LoansTransaction.amount,
        models.TransactionType.transactiontype_name,
        models.LoansTransaction.transaction_id,
        models.LoansTransaction.status
    ) \
        .all()

    return accounts_transaction


# Shares

# @router.get("/shareValue")
# async def ()
@router.get("/shform/{member_shares_acc_id}")
async def get_share_value(member_shares_acc_id: int,
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    shareValue = db.query(models.ShareAccount.share_value) \
        .select_from(models.MemberShareAccount) \
        .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .filter(models.MemberShareAccount.id == member_shares_acc_id) \
        .first()
    return shareValue


@router.post("/transaction/shares")
async def create_transactions_shares_acc(transactShare: SharesTransaction,
                                         user: dict = Depends(get_current_user),
                                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    shareValue = db.query(models.ShareAccount.share_value) \
        .select_from(models.ShareAccount) \
        .join(models.MemberShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .filter(models.MemberShareAccount.id == transactShare.shares_acc_id) \
        .first()

    stamp = transactShare.Amount * shareValue.share_value
    transactions_models = models.SharesTransaction()
    transactions_models.transactiontype_id = transactShare.transactiontype_id
    transactions_models.amount = stamp
    transactions_models.prep_by = user.get("id")
    transactions_models.narration = transactShare.narration
    transactions_models.shares_acc_id = transactShare.shares_acc_id
    transactions_models.transaction_date = datetime.now()

    db.add(transactions_models)
    db.flush()
    db.commit()

    return "Share Purchased"


@router.post("/transaction/share")
async def create_transactions_shares_acc_withdrawal(transactShare: SharesTransaction,
                                                    user: dict = Depends(get_current_user),
                                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    transactions_models = models.SharesTransaction()
    transactions_models.transactiontype_id = transactShare.transactiontype_id
    transactions_models.amount = transactShare.Amount
    transactions_models.prep_by = user.get("id")
    transactions_models.narration = transactShare.narration
    transactions_models.shares_acc_id = transactShare.shares_acc_id
    transactions_models.transaction_date = datetime.now()

    db.add(transactions_models)
    db.flush()
    db.commit()

    return "Share Withdrawn"


@router.get("/transaction/share/{member_shares_acc_id}")
async def get_one_shares_account_transactions(member_shares_acc_id: int,
                                              user: dict = Depends(get_current_user),
                                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    accounts_transaction = db.query(
        models.SharesTransaction.transaction_date,
        models.SharesTransaction.narration,
        models.Users.username,
        models.SharesTransaction.amount,
        models.TransactionType.transactiontype_name,
        models.SharesTransaction.transaction_id
    ).select_from(models.SharesTransaction) \
        .join(models.TransactionType,
              models.SharesTransaction.transactiontype_id == models.TransactionType.transactype_id) \
        .join(models.Users,
              models.Users.id == models.SharesTransaction.prep_by) \
        .filter(models.SharesTransaction.shares_acc_id == member_shares_acc_id) \
        .order_by(desc(models.SharesTransaction.transaction_id)) \
        .group_by(
        models.SharesTransaction.transaction_date,
        models.SharesTransaction.narration,
        models.Users.username,
        models.SharesTransaction.amount,
        models.TransactionType.transactiontype_name,
        models.SharesTransaction.transaction_id
    ) \
        .all()

    return accounts_transaction


@router.get("/mass/form/{association_id}")
async def mass_transaction_form(association_id: int,
                                user: dict = Depends(get_current_user),
                                db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    members = db.query(models.Members.firstname,
                       models.Members.lastname,
                       models.Members.member_id,
                       models.AssociationMembers.association_members_id) \
        .select_from(models.Association) \
        .join(models.AssociationMembers, models.Association.association_id == models.AssociationMembers.association_id) \
        .join(models.Members, models.Members.member_id == models.AssociationMembers.members_id) \
        .filter(models.Association.association_id == association_id) \
        .all()

    info = db.query(models.MemberSavingsAccount.id,
                    models.SavingsAccount.account_name) \
        .select_from(models.MemberSavingsAccount) \
        .join(models.SavingsAccount, models.MemberSavingsAccount.savings_id == models.SavingsAccount.id) \
        .all()

    return {"Members": members, "All_Accounts": info}


class TransferSavings(BaseModel):
    to_accountType: str
    Amount: float
    savings_acc_id: int
    to_member_account_id: int


@router.post("/transfer")
async def transfers_in_savings_account(tranfer: TransferSavings,
                                       user: dict = Depends(get_current_user),
                                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    if tranfer.to_accountType == "savings":
        to_acc = db.query(models.Members.firstname,
                          models.Members.lastname,
                          models.SavingsAccount.account_name, ) \
            .select_from(models.MemberSavingsAccount) \
            .join(models.Members, models.MemberSavingsAccount.member_id == models.Members.member_id) \
            .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
            .filter(models.MemberSavingsAccount.id == tranfer.to_member_account_id) \
            .first()

        from_acc = db.query(models.Members.firstname,
                            models.Members.lastname,
                            models.SavingsAccount.account_name,
                            models.MemberSavingsAccount.current_balance) \
            .select_from(models.MemberSavingsAccount) \
            .join(models.Members, models.MemberSavingsAccount.member_id == models.Members.member_id) \
            .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
            .filter(models.MemberSavingsAccount.id == tranfer.savings_acc_id) \
            .first()

        if tranfer.Amount <= from_acc.current_balance:
            transfer_from = models.SavingsTransaction()
            transfer_from.amount = tranfer.Amount
            transfer_from.narration = f"Transferred to: {to_acc.firstname} {to_acc.lastname}'s {to_acc.account_name} account"
            transfer_from.savings_acc_id = tranfer.savings_acc_id
            transfer_from.transactiontype_id = 2
            transfer_from.transaction_date = datetime.now()
            transfer_from.prep_by = user.get("id")
            db.add(transfer_from)
            db.commit()

            trn = models.SavingsTransaction()
            trn.transactiontype_id = 1
            trn.amount = tranfer.Amount
            trn.narration = f"Received from: {from_acc.firstname} {from_acc.lastname}'s {from_acc.account_name} account"
            trn.savings_acc_id = tranfer.to_member_account_id
            trn.prep_by = user.get("id")
            trn.transaction_date = datetime.now()
            db.add(trn)
            db.commit()

            return "Transfer Complete"
        else:
            raise insufficient_balance()

    elif tranfer.to_accountType == "loans":
        to_acc = db.query(models.Members.firstname,
                          models.Members.lastname,
                          models.LoanAccount.account_name) \
            .select_from(models.MemberLoanAccount) \
            .join(models.Members, models.MemberLoanAccount.member_id == models.Members.member_id) \
            .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
            .filter(models.MemberLoanAccount.id == tranfer.to_member_account_id) \
            .first()

        from_acc = db.query(models.Members.firstname,
                            models.Members.lastname,
                            models.SavingsAccount.account_name,
                            models.MemberSavingsAccount.current_balance) \
            .select_from(models.MemberSavingsAccount) \
            .join(models.Members, models.MemberSavingsAccount.member_id == models.Members.member_id) \
            .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
            .filter(models.MemberSavingsAccount.id == tranfer.savings_acc_id) \
            .first()

        if tranfer.Amount <= from_acc.current_balance:
            transfer_from = models.SavingsTransaction()
            transfer_from.amount = tranfer.Amount
            transfer_from.narration = f"Transferred to: {to_acc.firstname} {to_acc.lastname}'s {to_acc.account_name} account"
            transfer_from.savings_acc_id = tranfer.savings_acc_id
            transfer_from.transactiontype_id = 2
            transfer_from.transaction_date = datetime.now()
            transfer_from.prep_by = user.get("id")
            db.add(transfer_from)
            db.commit()

            trn_to = models.LoansTransaction()
            trn_to.transactiontype_id = 1
            trn_to.amount = tranfer.Amount
            trn_to.narration = f"Paid from: {from_acc.firstname} {from_acc.lastname}'s {from_acc.account_name} account"
            trn_to.loans_acc_id = tranfer.to_member_account_id
            trn_to.prep_by = user.get("id")
            trn_to.transaction_date = datetime.now()
            trn_to.status = "Pay off"
            db.add(trn_to)
            db.commit()
            return "Transfer Complete"
        else:
            raise insufficient_balance()

    elif tranfer.to_accountType == "shares":
        to_acc = db.query(models.Members.firstname,
                          models.Members.lastname,
                          models.ShareAccount.account_name) \
            .select_from(models.MemberShareAccount) \
            .join(models.Members, models.MemberShareAccount.member_id == models.Members.member_id) \
            .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
            .filter(models.MemberShareAccount.id == tranfer.to_member_account_id) \
            .first()

        from_acc = db.query(models.Members.firstname,
                            models.Members.lastname,
                            models.SavingsAccount.account_name,
                            models.MemberSavingsAccount.current_balance) \
            .select_from(models.MemberSavingsAccount) \
            .join(models.Members, models.MemberSavingsAccount.member_id == models.Members.member_id) \
            .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
            .filter(models.MemberSavingsAccount.id == tranfer.savings_acc_id) \
            .first()

    if tranfer.Amount <= from_acc.current_balance:
        transfer_from = models.SavingsTransaction()
        transfer_from.amount = tranfer.Amount
        transfer_from.narration = f"Transferred to: {to_acc.firstname} {to_acc.lastname}'s {to_acc.account_name} account"
        transfer_from.savings_acc_id = tranfer.savings_acc_id
        transfer_from.transactiontype_id = 2
        transfer_from.transaction_date = datetime.now()
        transfer_from.prep_by = user.get("id")
        db.add(transfer_from)
        db.commit()

        trn_to = models.SharesTransaction()
        trn_to.transactiontype_id = 1
        trn_to.amount = tranfer.Amount
        trn_to.narration = f"Purchased from: {from_acc.firstname} {from_acc.lastname}'s {from_acc.account_name} account"
        trn_to.shares_acc_id = tranfer.to_member_account_id
        trn_to.prep_by = user.get("id")
        trn_to.transaction_date = datetime.now()
        db.add(trn_to)
        db.commit()
        return f"Transfer Complete"
    else:
        raise insufficient_balance()


@router.get("transfer/info/{member_id}")
async def get_info_for_transfer(member_id,
                                user: dict = Depends(get_current_user),
                                db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    # Savings Accounts
    all_savings = db.query(models.MemberSavingsAccount.id,
                           models.Members.firstname,
                           models.Members.lastname,
                           models.Association.association_name,
                           models.SavingsAccount.account_name) \
        .select_from(models.MemberSavingsAccount) \
        .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_members_id == models.MemberSavingsAccount.association_member_id) \
        .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.MemberSavingsAccount.member_id != member_id) \
        .all()

    individual_accounts = db.query(models.MemberSavingsAccount.id,
                                   models.Members.firstname,
                                   models.Members.lastname,
                                   models.SavingsAccount.account_name) \
        .select_from(models.MemberSavingsAccount) \
        .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .outerjoin(models.AssociationMembers, models.Members.member_id == models.AssociationMembers.members_id) \
        .filter(models.AssociationMembers.members_id.is_(None)) \
        .filter(models.MemberSavingsAccount.member_id != member_id) \
        .all()

    my_savings = db.query(models.MemberSavingsAccount.id,
                          models.Association.association_name,
                          models.SavingsAccount.account_name) \
        .select_from(models.MemberSavingsAccount) \
        .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_members_id == models.MemberSavingsAccount.association_member_id) \
        .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.MemberSavingsAccount.member_id == member_id) \
        .all()

    # Loans Accounts

    all_loans = db.query(models.MemberLoanAccount.id,
                         models.Members.firstname,
                         models.Members.lastname,
                         models.Association.association_name,
                         models.LoanAccount.account_name) \
        .select_from(models.MemberLoanAccount) \
        .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
        .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_members_id == models.MemberLoanAccount.association_member_id) \
        .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.MemberLoanAccount.member_id != member_id) \
        .all()

    individual_loan_accounts = db.query(models.MemberLoanAccount.id,
                                        models.Members.firstname,
                                        models.Members.lastname,
                                        models.LoanAccount.account_name) \
        .select_from(models.MemberLoanAccount) \
        .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
        .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
        .outerjoin(models.AssociationMembers, models.Members.member_id == models.AssociationMembers.members_id) \
        .filter(models.AssociationMembers.members_id.is_(None)) \
        .filter(models.MemberLoanAccount.member_id != member_id) \
        .all()

    my_loans = db.query(models.MemberLoanAccount.id,
                        models.Association.association_name,
                        models.LoanAccount.account_name) \
        .select_from(models.MemberLoanAccount) \
        .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
        .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_members_id == models.MemberLoanAccount.association_member_id) \
        .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.MemberLoanAccount.member_id == member_id) \
        .all()

    # Shares Accounts

    all_shares = db.query(models.MemberShareAccount.id,
                          models.Members.firstname,
                          models.Members.lastname,
                          models.Association.association_name,
                          models.ShareAccount.account_name) \
        .select_from(models.MemberShareAccount) \
        .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
        .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_members_id == models.MemberShareAccount.association_member_id) \
        .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.MemberShareAccount.member_id != member_id) \
        .all()

    individual_share_accounts = db.query(models.MemberShareAccount.id,
                                         models.Members.firstname,
                                         models.Members.lastname,
                                         models.ShareAccount.account_name) \
        .select_from(models.MemberShareAccount) \
        .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
        .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .outerjoin(models.AssociationMembers, models.Members.member_id == models.AssociationMembers.members_id) \
        .filter(models.AssociationMembers.members_id.is_(None)) \
        .filter(models.MemberShareAccount.member_id != member_id) \
        .all()

    my_shares = db.query(models.MemberShareAccount.id,
                         models.Association.association_name,
                         models.ShareAccount.account_name) \
        .select_from(models.MemberShareAccount) \
        .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
        .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_members_id == models.MemberShareAccount.association_member_id) \
        .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.MemberShareAccount.member_id == member_id) \
        .all()

    return {
        "All_Savings_Acc": all_savings,
        "My_Savings_Acc": my_savings,
        "Individual_Acc": individual_accounts,
        "All_Loans_Acc": all_loans,
        "My_Loans_Acc": my_loans,
        "Individual_Loans_Acc": individual_loan_accounts,
        "All_Shares_Acc": all_shares,
        "My_Shares_Acc": my_shares,
        "Individual_Shares_Acc": individual_share_accounts
    }


def insufficient_balance():
    error_nkoa = HTTPException(
        status_code=status.HTTP_417_EXPECTATION_FAILED,
        detail="Insufficient Balance to perform transfer",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return error_nkoa



