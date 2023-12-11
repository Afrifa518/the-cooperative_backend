import sys

from sqlalchemy import desc, func, and_, asc

sys.path.append("../..")

from typing import Optional, List, Union
from fastapi import Depends, HTTPException, APIRouter, status, Form
from dateutil.relativedelta import relativedelta
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
import base64
from .auth import get_current_user, get_user_exception
from datetime import datetime, timedelta

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
    transaction_id: Optional[int]
    balance: Optional[float]
    decide: Optional[str]


class SavingTransaction(BaseModel):
    transactiontype_idd: int
    Amountt: float
    narrationn: Optional[str]
    savings_acc_idd: int


class SavingTransactionnEdit(BaseModel):
    transaction_id: int
    transactiontype_idd: int
    Amountt: float
    narrationn: Optional[str]
    savings_acc_idd: int
    date: str


class SavingTransactionEdit(BaseModel):
    transaction_id: int
    Amount: float
    narration: Optional[str]
    savings_acc_id: int
    balance: Optional[float]
    date: str


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
    period: float
    on_due_date: str
    spending_means: str
    account_name: str


# Savings

@router.post("/transaction/savings")
async def create_transactions_savings_acc(transactSave: SavingsTransaction,
                                          user: dict = Depends(get_current_user),
                                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    results = await check_for_stamps_and_cash(member_savings_acc=transactSave.savings_acc_id, user=user, db=db)

    stsvya = db.query(models.SavingsAccount) \
        .select_from(models.MemberSavingsAccount) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .filter(models.MemberSavingsAccount.id == transactSave.savings_acc_id) \
        .first()

    prev_balance = db.query(models.MemberSavingsAccount).filter(
        models.MemberSavingsAccount.id == transactSave.savings_acc_id).first()
    # print(transactSave.decide)
    if transactSave.decide == "Use Stamps":
        stamp = transactSave.Amount * stsvya.stamp_value
    else:
        stamp = transactSave.Amount
    if transactSave.decide == "Use Stamps":
        transactions_models = models.SavingsTransaction()
        transactions_models.transactiontype_id = transactSave.transactiontype_id
        transactions_models.amount = stamp
        transactions_models.prep_by = user.get("id")
        transactions_models.narration = transactSave.narration
        transactions_models.savings_acc_id = transactSave.savings_acc_id
        transactions_models.transaction_date = datetime.now()
        transactions_models.balance = prev_balance.current_balance + stamp
    else:
        transactions_models = models.SavingsTransaction()
        transactions_models.transactiontype_id = transactSave.transactiontype_id
        transactions_models.amount = transactSave.Amount
        transactions_models.prep_by = user.get("id")
        transactions_models.narration = transactSave.narration
        transactions_models.savings_acc_id = transactSave.savings_acc_id
        transactions_models.transaction_date = datetime.now()
        transactions_models.balance = prev_balance.current_balance + transactSave.Amount

    if transactSave.transactiontype_id == 2:
        association_id = db.query(models.Association) \
            .select_from(models.Association) \
            .join(models.AssociationMembers,
                  models.AssociationMembers.association_id == models.Association.association_id) \
            .join(models.MemberSavingsAccount,
                  models.MemberSavingsAccount.association_member_id == models.AssociationMembers.association_members_id) \
            .filter(models.MemberSavingsAccount.id == transactSave.savings_acc_id) \
            .first()
        current_date = datetime.now()
        today_date = current_date.strftime('%Y-%m-%d')

        today = db.query(models.MomoAccountAssociation) \
            .filter(models.MomoAccountAssociation.date == today_date,
                    models.MomoAccountAssociation.association_id == association_id.association_id) \
            .first()
        if today:
            if transactSave.decide == "Use Stamps":
                today.momo_bal -= stamp
            else:
                today.momo_bal -= transactSave.Amount
            db.commit()

    db.add(transactions_models)
    db.flush()
    db.commit()
    return "Transaction Complete"


@router.delete("/transaction/savings/{transaction_id}")
async def delete_transactions_savings(transaction_id: int,
                                      user: dict = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    db.query(models.SavingsTransaction).filter(models.SavingsTransaction.transaction_id == transaction_id).delete()
    db.commit()
    return "Transaction Deleted"


@router.delete("/transaction/loans/{transaction_id}")
async def delete_transactions_loans(transaction_id: int,
                                    user: dict = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    db.query(models.LoansTransaction).filter(models.LoansTransaction.transaction_id == transaction_id).delete()
    db.commit()
    return "Transaction Deleted"


@router.delete("/transaction/shares/{transaction_id}")
async def delete_transactions_shares(transaction_id: int,
                                     user: dict = Depends(get_current_user),
                                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    db.query(models.SharesTransaction).filter(models.SharesTransaction.transaction_id == transaction_id).delete()
    db.commit()
    return "Transaction Deleted"


@router.post("/transaction/withdraw")
async def create_transactions_withdrawals_savings_acc(transactSavee: SavingTransaction,
                                                      user: dict = Depends(get_current_user),
                                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberSavingsAccount).filter(
        models.MemberSavingsAccount.id == transactSavee.savings_acc_idd).first()

    transactions_models = models.SavingsTransaction()
    transactions_models.transactiontype_id = transactSavee.transactiontype_idd
    transactions_models.amount = transactSavee.Amountt
    transactions_models.prep_by = user.get("id")
    transactions_models.narration = transactSavee.narrationn
    transactions_models.savings_acc_id = transactSavee.savings_acc_idd
    transactions_models.transaction_date = datetime.now()
    transactions_models.balance = prev_balance.current_balance - transactSavee.Amountt

    db.add(transactions_models)
    db.flush()
    db.commit()

    return "Withdraw Successful"


@router.post("/transaction/edit")
async def edit_transactions_savings_acc(transactSavee: SavingTransactionEdit,
                                        user: dict = Depends(get_current_user),
                                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberSavingsAccount).filter(
        models.MemberSavingsAccount.id == transactSavee.savings_acc_id).first()

    testam = db.query(models.SavingsTransaction).filter(
        models.SavingsTransaction.transaction_id == transactSavee.transaction_id).first()

    amount_difference = transactSavee.Amount - testam.amount
    if transactSavee.date:
        update_data = {
            models.SavingsTransaction.amount: transactSavee.Amount,
            models.SavingsTransaction.narration: transactSavee.narration,
            models.SavingsTransaction.balance: models.SavingsTransaction.balance + amount_difference,
            models.SavingsTransaction.transaction_date: transactSavee.date
        }
        transact = db.query(models.SavingsTransaction).filter(
            models.SavingsTransaction.transaction_id == transactSavee.transaction_id).update(update_data)
    else:
        date = testam.transaction_date
        update_data = {
            models.SavingsTransaction.amount: transactSavee.Amount,
            models.SavingsTransaction.narration: transactSavee.narration,
            models.SavingsTransaction.balance: models.SavingsTransaction.balance + amount_difference,
            models.SavingsTransaction.transaction_date: date
        }
        transact = db.query(models.SavingsTransaction).filter(
            models.SavingsTransaction.transaction_id == transactSavee.transaction_id).update(update_data)

    balance_update = db.query(models.SavingsTransaction) \
        .filter(and_(
        models.SavingsTransaction.transaction_date > testam.transaction_date,
        models.SavingsTransaction.transaction_id != transactSavee.transaction_id
    )).all()

    for transaction in balance_update:
        if transaction.balance:
            transaction.balance = transaction.balance + amount_difference
        else:
            transaction.balance = amount_difference
    db.flush()
    db.commit()

    balance = db.query(models.SavingsTransaction) \
        .filter(models.SavingsTransaction.savings_acc_id == transactSavee.savings_acc_id) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .first()
    prev_balance.current_balance = balance.balance
    db.commit()

    return "Transaction Updated"


@router.post("/transaction/edit/loan")
async def edit_transactions_loans_acc(transactSavee: SavingTransactionEdit,
                                      user: dict = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberLoanAccount).filter(
        models.MemberLoanAccount.id == transactSavee.savings_acc_id).first()

    testam = db.query(models.LoansTransaction).filter(
        models.LoansTransaction.transaction_id == transactSavee.transaction_id).first()

    amount_difference = transactSavee.Amount - testam.amount
    if testam.status == "Request" or testam.status == "Pay off":
        if transactSavee.date:
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amount,
                models.LoansTransaction.narration: transactSavee.narration,
                models.LoansTransaction.balance: models.LoansTransaction.balance + amount_difference,
                models.LoansTransaction.transaction_date: transactSavee.date
            }
        else:
            date = testam.transaction_date
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amount,
                models.LoansTransaction.narration: transactSavee.narration,
                models.LoansTransaction.balance: models.LoansTransaction.balance + amount_difference,
                models.LoansTransaction.transaction_date: date
            }
    else:
        if transactSavee.date:
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amount,
                models.LoansTransaction.narration: transactSavee.narration,
                models.LoansTransaction.transaction_date: transactSavee.date
            }
        else:
            date = testam.transaction_date
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amount,
                models.LoansTransaction.narration: transactSavee.narration,
                models.LoansTransaction.transaction_date: date
            }

    transact = db.query(models.LoansTransaction).filter(
        models.LoansTransaction.transaction_id == transactSavee.transaction_id).update(update_data)

    balance_update = db.query(models.LoansTransaction) \
        .filter(and_(
        models.LoansTransaction.transaction_date > testam.transaction_date,
        models.LoansTransaction.transaction_id != transactSavee.transaction_id
    )).all()

    for transaction in balance_update:
        if transaction.balance:
            transaction.balance = transaction.balance + amount_difference
        else:
            transaction.balance = amount_difference
    db.flush()
    db.commit()

    balance = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.loans_acc_id == transactSavee.savings_acc_id) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .first()
    prev_balance.current_balance = balance.balance
    db.commit()

    return "Transaction Updated"


@router.post("/transaction/other/edit/loan")
async def edit_transactions_other_loans_acc(transactSavee: SavingTransactionnEdit,
                                            user: dict = Depends(get_current_user),
                                            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberLoanAccount).filter(
        models.MemberLoanAccount.id == transactSavee.savings_acc_idd).first()

    testam = db.query(models.LoansTransaction).filter(
        models.LoansTransaction.transaction_id == transactSavee.transaction_id).first()

    amount_difference = transactSavee.Amountt - testam.amount
    if transactSavee.date:
        if testam.status == "Request":
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amountt,
                models.LoansTransaction.narration: transactSavee.narrationn,
                models.LoansTransaction.balance: models.LoansTransaction.balance - amount_difference,
                models.LoansTransaction.transaction_date: transactSavee.date
            }
        else:
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amountt,
                models.LoansTransaction.narration: transactSavee.narrationn,
                models.LoansTransaction.transaction_date: transactSavee.date
            }
    else:
        date = testam.transaction_date
        if testam.status == "Request":
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amountt,
                models.LoansTransaction.narration: transactSavee.narrationn,
                models.LoansTransaction.balance: models.LoansTransaction.balance - amount_difference,
                models.LoansTransaction.transaction_date: date
            }
        else:
            update_data = {
                models.LoansTransaction.amount: transactSavee.Amountt,
                models.LoansTransaction.narration: transactSavee.narrationn,
                models.LoansTransaction.transaction_date: date
            }
    transact = db.query(models.LoansTransaction).filter(
        models.LoansTransaction.transaction_id == transactSavee.transaction_id).update(update_data)

    balance_update = db.query(models.LoansTransaction) \
        .filter(and_(
        models.LoansTransaction.transaction_date > testam.transaction_date,
        models.LoansTransaction.transaction_id != transactSavee.transaction_id
    )).all()

    for transaction in balance_update:
        if transaction.balance:
            transaction.balance = transaction.balance + amount_difference
        else:
            transaction.balance = amount_difference
    db.flush()
    db.commit()
    balance = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.loans_acc_id == transactSavee.savings_acc_idd) \
        .order_by(desc(models.LoansTransaction.transaction_id)) \
        .first()
    prev_balance.current_balance = balance.balance
    db.commit()

    return "Transaction Updated"


@router.post("/transaction/other/edit")
async def edit_transactions_other_savings_acc(transactSavee: SavingTransactionnEdit,
                                              user: dict = Depends(get_current_user),
                                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberSavingsAccount).filter(
        models.MemberSavingsAccount.id == transactSavee.savings_acc_idd).first()

    testam = db.query(models.SavingsTransaction).filter(
        models.SavingsTransaction.transaction_id == transactSavee.transaction_id).first()

    amount_difference = transactSavee.Amountt - testam.amount
    if transactSavee.date:
        update_data = {
            models.SavingsTransaction.amount: transactSavee.Amountt,
            models.SavingsTransaction.narration: transactSavee.narrationn,
            models.SavingsTransaction.balance: models.SavingsTransaction.balance - amount_difference,
            models.SavingsTransaction.transaction_date: transactSavee.date
        }
    else:
        date = testam.transaction_date
        update_data = {
            models.SavingsTransaction.amount: transactSavee.Amountt,
            models.SavingsTransaction.narration: transactSavee.narrationn,
            models.SavingsTransaction.balance: models.SavingsTransaction.balance - amount_difference,
            models.SavingsTransaction.transaction_date: date
        }

    transact = db.query(models.SavingsTransaction).filter(
        models.SavingsTransaction.transaction_id == transactSavee.transaction_id).update(update_data)

    balance_update = db.query(models.SavingsTransaction) \
        .filter(and_(
        models.SavingsTransaction.transaction_date > testam.transaction_date,
        models.SavingsTransaction.transaction_id != transactSavee.transaction_id
    )).all()

    for transaction in balance_update:
        if transaction.balance:
            transaction.balance = transaction.balance + amount_difference
        else:
            transaction.balance = amount_difference

    db.flush()
    db.commit()
    balance = db.query(models.SavingsTransaction) \
        .filter(models.SavingsTransaction.savings_acc_id == transactSavee.savings_acc_idd) \
        .order_by(desc(models.SavingsTransaction.transaction_id)) \
        .first()
    prev_balance.current_balance = balance.balance
    db.commit()

    return "Transaction Updated"


@router.post("/transaction/share")
async def edit_transactions_share_acc(transactSavee: SavingTransactionEdit,
                                      user: dict = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberShareAccount).filter(
        models.MemberShareAccount.id == transactSavee.savings_acc_id).first()

    testam = db.query(models.SharesTransaction).filter(
        models.SharesTransaction.transaction_id == transactSavee.transaction_id).first()

    amount_difference = transactSavee.Amount + testam.amount
    if transactSavee.date:
        update_data = {
            models.SharesTransaction.amount: transactSavee.Amount,
            models.SharesTransaction.narration: transactSavee.narration,
            models.SharesTransaction.balance: models.SharesTransaction.balance + amount_difference,
            models.SharesTransaction.transaction_date: transactSavee.date
        }
    else:
        date = testam.transaction_date
        update_data = {
            models.SharesTransaction.amount: transactSavee.Amount,
            models.SharesTransaction.narration: transactSavee.narration,
            models.SharesTransaction.balance: models.SharesTransaction.balance + amount_difference,
            models.SharesTransaction.transaction_date: date
        }
    transact = db.query(models.SharesTransaction).filter(
        models.SharesTransaction.transaction_id == transactSavee.transaction_id).update(update_data)

    balance_update = db.query(models.SharesTransaction) \
        .filter(and_(
        models.SharesTransaction.transaction_date > testam.transaction_date,
        models.SharesTransaction.transaction_id != transactSavee.transaction_id
    )).all()

    for transaction in balance_update:
        if transaction.balance:
            transaction.balance = transaction.balance + amount_difference
        else:
            transaction.balance = amount_difference
    db.flush()
    db.commit()
    balance = db.query(models.SharesTransaction) \
        .filter(models.SharesTransaction.shares_acc_id == transactSavee.savings_acc_id) \
        .order_by(desc(models.SharesTransaction.transaction_id)) \
        .first()
    prev_balance.current_balance = balance.balance
    db.commit()

    return "Transaction Updated"


@router.post("/transaction/other/edit/share")
async def edit_transactions_other_share_acc(transactSavee: SavingTransactionnEdit,
                                            user: dict = Depends(get_current_user),
                                            db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberShareAccount).filter(
        models.MemberShareAccount.id == transactSavee.savings_acc_idd).first()

    testam = db.query(models.SharesTransaction).filter(
        models.SharesTransaction.transaction_id == transactSavee.transaction_id).first()

    amount_difference = transactSavee.Amountt - testam.amount
    if transactSavee.date:
        update_data = {
            models.SharesTransaction.amount: transactSavee.Amountt,
            models.SharesTransaction.narration: transactSavee.narrationn,
            models.SharesTransaction.balance: models.SharesTransaction.balance - amount_difference,
            models.SharesTransaction.transaction_date: transactSavee.date
        }
    else:
        date = testam.transaction_date
        update_data = {
            models.SharesTransaction.amount: transactSavee.Amountt,
            models.SharesTransaction.narration: transactSavee.narrationn,
            models.SharesTransaction.balance: models.SharesTransaction.balance - amount_difference,
            models.SharesTransaction.transaction_date: date
        }
    transact = db.query(models.SharesTransaction).filter(
        models.SharesTransaction.transaction_id == transactSavee.transaction_id).update(update_data)

    balance_update = db.query(models.SharesTransaction) \
        .filter(and_(
        models.SharesTransaction.transaction_date > testam.transaction_date,
        models.SharesTransaction.transaction_id != transactSavee.transaction_id
    )).all()

    for transaction in balance_update:
        if transaction.balance:
            transaction.balance = transaction.balance + amount_difference
        else:
            transaction.balance = amount_difference
    db.flush()
    db.commit()
    balance = db.query(models.SharesTransaction) \
        .filter(models.SharesTransaction.shares_acc_id == transactSavee.savings_acc_idd) \
        .order_by(desc(models.SharesTransaction.transaction_id)) \
        .first()
    prev_balance.current_balance = balance.balance
    db.commit()

    return "Transaction Updated"


class SocietyTransaction(BaseModel):
    transactiontype_id: int
    amount: float
    narration: Optional[str]
    society_account_id: int


@router.post("/transaction/withdraw/society")
async def create_transactions_society_acc(societyTransaction: SocietyTransaction,
                                          user: dict = Depends(get_current_user),
                                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.SocietyBankAccounts).filter(
        models.SocietyBankAccounts.id == societyTransaction.society_account_id).first()
    if societyTransaction.transactiontype_id == 2:
        transactions_models = models.SocietyTransactions()
        transactions_models.transactiontype_id = societyTransaction.transactiontype_id
        transactions_models.amount = societyTransaction.amount
        transactions_models.transaction_date = datetime.now()
        transactions_models.balance = prev_balance.current_balance - societyTransaction.amount
        transactions_models.prep_by = user.get("id")
        transactions_models.society_account_id = societyTransaction.society_account_id
        transactions_models.narration = societyTransaction.narration
    elif societyTransaction.transactiontype_id == 1:
        transactions_models = models.SocietyTransactions()
        transactions_models.transactiontype_id = societyTransaction.transactiontype_id
        transactions_models.amount = societyTransaction.amount
        transactions_models.transaction_date = datetime.now()
        transactions_models.balance = prev_balance.current_balance + societyTransaction.amount
        transactions_models.prep_by = user.get("id")
        transactions_models.society_account_id = societyTransaction.society_account_id
        transactions_models.narration = societyTransaction.narration
    else:
        raise HTTPException(status_code=status.WS_1013_TRY_AGAIN_LATER, detail="Transaction was not successful")

    db.add(transactions_models)
    db.flush()
    db.commit()

    return "Transaction Successful"


@router.get("/transactions/society/{society_acc_id}")
async def get_society_acc_transactions(society_acc_id: int,
                                       user: dict = Depends(get_current_user),
                                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    tra = db.query(models.SocietyTransactions.transaction_id,
                   models.SocietyTransactions.transaction_date,
                   models.SocietyTransactions.amount,
                   models.SocietyTransactions.transactiontype_id,
                   models.SocietyTransactions.narration,
                   models.SocietyTransactions.balance,
                   models.Users.username) \
        .select_from(models.SocietyTransactions) \
        .join(models.Users,
              models.SocietyTransactions.prep_by == models.Users.id) \
        .filter(models.SocietyTransactions.society_account_id == society_acc_id) \
        .order_by(desc(models.SocietyTransactions.transaction_date)) \
        .all()

    return tra


class SocietTransfer(BaseModel):
    to_account_id: int
    amount: float
    society_account_id: int


@router.post("/society/transfer")
async def transfer_in_society_account(transfer: SocietTransfer,
                                      user: dict = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    to_acc = db.query(models.SocietyBankAccounts) \
        .filter(models.SocietyBankAccounts.id == transfer.to_account_id) \
        .first()
    from_acc = db.query(models.SocietyBankAccounts) \
        .filter(models.SocietyBankAccounts.id == transfer.society_account_id) \
        .first()

    if transfer.amount <= from_acc.current_balance:
        transfer_from = models.SocietyTransactions(
            transactiontype_id=2,
            amount=transfer.amount,
            transaction_date=datetime.now(),
            balance=from_acc.current_balance - transfer.amount,
            prep_by=user.get("id"),
            society_account_id=transfer.society_account_id,
            narration=f"Transferred to: {to_acc.account_name} bank account",
        )
        db.add(transfer_from)
        db.commit()

        transfer_to = models.SocietyTransactions(
            transactiontype_id=1,
            amount=transfer.amount,
            transaction_date=datetime.now(),
            balance=to_acc.current_balance + transfer.amount,
            prep_by=user.get("id"),
            society_account_id=transfer.to_account_id,
            narration=f"Received from: {from_acc.account_name} bank account",
        )
        db.add(transfer_to)
        db.commit()

        return "Transfer Complete"
    else:
        raise insufficient_balance()


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

    stampOrCash = db.query(models.SavingsAccount) \
        .select_from(models.MemberSavingsAccount) \
        .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .filter(models.MemberSavingsAccount.id == member_savings_acc) \
        .first()

    if stampOrCash.stamp_value:
        dta = stampOrCash
        return dta
    else:
        return "Using Cash"
    # return stampOrCash


@router.post("/transaction/member_savings_acc_id")
async def get_one_savings_accounts_transactions(member_savings_acc_id: int = Form(...),
                                                start_date: Optional[str] = Form(None),
                                                end_date: Optional[str] = Form(None),
                                                user: dict = Depends(get_current_user),
                                                db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    total_with = 0
    total_dep = 0

    if start_date is None:
        accounts_transaction = db.query(
            models.SavingsTransaction.transaction_date,
            models.SavingsTransaction.narration,
            models.Users.username,
            models.SavingsTransaction.amount,
            models.TransactionType.transactiontype_name,
            models.SavingsTransaction.transaction_id,
            models.SavingsTransaction.balance
        ).select_from(models.SavingsTransaction) \
            .join(models.TransactionType,
                  models.SavingsTransaction.transactiontype_id == models.TransactionType.transactype_id) \
            .join(models.Users,
                  models.Users.id == models.SavingsTransaction.prep_by) \
            .filter(models.SavingsTransaction.savings_acc_id == member_savings_acc_id) \
            .order_by(desc(models.SavingsTransaction.transaction_date)) \
            .all()
    else:
        accounts_transaction = db.query(
            models.SavingsTransaction.transaction_date,
            models.SavingsTransaction.narration,
            models.Users.username,
            models.SavingsTransaction.amount,
            models.TransactionType.transactiontype_name,
            models.SavingsTransaction.transaction_id,
            models.SavingsTransaction.balance
        ).select_from(models.SavingsTransaction) \
            .join(models.TransactionType,
                  models.SavingsTransaction.transactiontype_id == models.TransactionType.transactype_id) \
            .join(models.Users,
                  models.Users.id == models.SavingsTransaction.prep_by) \
            .filter(models.SavingsTransaction.savings_acc_id == member_savings_acc_id,
                    func.date(models.SavingsTransaction.transaction_date) >= start_date,
                    func.date(models.SavingsTransaction.transaction_date) <= end_date) \
            .order_by(desc(models.SavingsTransaction.transaction_date)) \
            .all()

    for item in accounts_transaction:
        if item.transactiontype_name == "Deposit":
            total_dep += item.amount
        elif item.transactiontype_name == "Withdraw":
            total_with += item.amount

    return {
        "data": accounts_transaction,
        "total_dep": total_dep,
        "total_wit": total_with
    }




# Loans

@router.post("/transaction/loans")
async def create_transactions_loans_request_acc(transactLoan: LoansTransaction,
                                                user: dict = Depends(get_current_user),
                                                db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    prev_balance = db.query(models.MemberLoanAccount).filter(
        models.MemberLoanAccount.id == transactLoan.loans_acc_id).first()

    transactions_models = models.LoansTransaction()
    transactions_models.transactiontype_id = transactLoan.transactiontype_id
    transactions_models.amount = transactLoan.Amount
    transactions_models.prep_by = user.get("id")
    transactions_models.narration = transactLoan.narration
    transactions_models.loans_acc_id = transactLoan.loans_acc_id
    transactions_models.transaction_date = datetime.now()

    if transactLoan.transactiontype_id == 2:
        transactions_models.status = "Requested"
        transactions_models.balance = prev_balance.current_balance
    elif transactLoan.transactiontype_id == 1:
        transactions_models.status = "Pay off"
        transactions_models.balance = prev_balance.current_balance + transactLoan.Amount
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


@router.get("/member/for_approval/{transaction_id}")
async def get_member_for_approval(transaction_id: int,
                                  user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    fg = db.query(models.Members.phone,
                  models.Members.member_id,
                  models.Members.firstname,
                  models.Members.lastname,
                  models.LoansTransaction.message,
                  models.LoansTransaction.status) \
        .select_from(models.MemberLoanAccount) \
        .join(models.LoansTransaction,
              models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .join(models.Members,
              models.Members.member_id == models.MemberLoanAccount.member_id) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()
    db.commit()

    associations = db.query(models.Association.association_name) \
        .join(models.AssociationMembers,
              models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.AssociationMembers.members_id == fg.member_id) \
        .all()

    # Savings Details
    account_savings = db.query(models.MemberSavingsAccount) \
        .select_from(models.MemberSavingsAccount) \
        .filter(models.MemberSavingsAccount.member_id == fg.member_id) \
        .all()

    total_savings_account_balance = 0

    for item in account_savings:
        total_savings_account_balance += item.current_balance

    # Loans Details
    account_loan = db.query(models.MemberLoanAccount) \
        .select_from(models.MemberLoanAccount) \
        .filter(models.MemberLoanAccount.member_id == fg.member_id) \
        .all()

    total_loans_account_balance = 0

    for item in account_loan:
        if item.current_balance is None:
            total_loans_account_balance += 0.0
        else:
            total_loans_account_balance += item.current_balance

    # Shares Details
    account_share = db.query(models.MemberShareAccount) \
        .select_from(models.MemberShareAccount) \
        .filter(models.MemberShareAccount.member_id == fg.member_id) \
        .all()

    total_share_account_balance = 0

    for item in account_share:
        total_share_account_balance += item.current_balance
    # print(type(fg), type(total_savings_account_balance), type(total_loans_account_balance),
    #       type(total_share_account_balance), type(associations))
    return {
        "Member_Details": fg,
        "Savings_Account_Balance": total_savings_account_balance,
        "Loans_Account_Balance": total_loans_account_balance,
        "Shares_Account_Balance": total_share_account_balance,
        "associations": associations
    }


@router.patch("/disapprove/loan/now")
async def disapprove_loan(transaction_id: int = Form(...),
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    update_data = {
        models.LoansTransaction.status: 'Requested'
    }
    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .update(update_data)
    db.commit()

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    return "Loan Disapproved"


@router.patch("/approve/loan")
async def approve_loan(transaction_id: int = Form(...),
                       approval_message: Optional[str] = Form(None),
                       user: dict = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    update_data = {
        models.LoansTransaction.status: 'Approved',
        models.LoansTransaction.message: approval_message
    }

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .update(update_data)

    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.commit()

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    return "Loan Approved"


def calculate_month_difference(start_date, end_date):
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


@router.patch("/disburse/loan")
async def disburse_loan(transaction_id: int = Form(...),
                        repayment_starts: str = Form(...),
                        num_of_weeks_to_end_payment: int = Form(...),
                        repaymentTimes: str = Form(...),
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    if repaymentTimes == "weeks":
        start_date = datetime.strptime(repayment_starts, '%Y-%m-%d')
        repayment_end_datee = start_date + timedelta(weeks=num_of_weeks_to_end_payment)
        repayment_end_date = repayment_end_datee.strftime('%Y-%m-%d')
    elif repaymentTimes == "months":
        start_date = datetime.strptime(repayment_starts, '%Y-%m-%d')
        repayment_end_datee = start_date + timedelta(weeks=num_of_weeks_to_end_payment * 4)
        repayment_end_date = repayment_end_datee.strftime('%Y-%m-%d')
    else:
        raise Exception('Could not process payment')

    loanTransaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    if repaymentTimes == "weeks":
        update_data = {
            models.LoansTransaction.status: 'Disbursed',
            models.LoansTransaction.repayment_starts: repayment_starts,
            models.LoansTransaction.repayment_ends: repayment_end_date,
            models.LoansTransaction.time: 'weeks'
        }
    else:
        update_data = {
            models.LoansTransaction.status: 'Disbursed',
            models.LoansTransaction.repayment_starts: repayment_starts,
            models.LoansTransaction.repayment_ends: repayment_end_date,
            models.LoansTransaction.time: 'months'
        }

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .update(update_data)
    db.commit()

    transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    coorp = db.query(models.MemberSavingsAccount) \
        .select_from(models.MemberLoanAccount) \
        .join(models.Members,
              models.Members.member_id == models.MemberLoanAccount.member_id) \
        .join(models.MemberSavingsAccount,
              models.MemberSavingsAccount.member_id == models.Members.member_id) \
        .filter(models.MemberLoanAccount.id == transaction.loans_acc_id,
                models.MemberSavingsAccount.savings_id == 1,
                models.MemberSavingsAccount.association_member_id == models.MemberLoanAccount.association_member_id) \
        .first()

    balance_account = db.query(models.MemberLoanAccount) \
        .filter(models.MemberLoanAccount.id == transaction.loans_acc_id) \
        .first()

    app_pro_fee = db.query(models.LoanAccount) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.loan_id == models.LoanAccount.id) \
        .filter(models.MemberLoanAccount.id == transaction.loans_acc_id) \
        .first()

    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime('%Y-%m-%d')

    pro_fee = (app_pro_fee.proccessing_fee / 100) * loanTransaction.amount
    app_fee = (app_pro_fee.application_fee / 100) * loanTransaction.amount

    charges = models.SavingsTransaction()
    charges.transactiontype_id = 2
    charges.amount = pro_fee + app_fee
    charges.prep_by = user.get("id")
    charges.narration = f"Debit for Application fee + Processing fee for disbursed on {formatted_date}"
    charges.transaction_date = datetime.now()
    charges.savings_acc_id = coorp.id

    db.add(charges)
    db.flush()
    db.commit()

    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # start_date = datetime.strptime(repayment_starts, '%Y-%m-%d')
    end_date = datetime.strptime(repayment_end_date, '%Y-%m-%d')
    if repaymentTimes == "weeks":
        months_difference = calculate_month_difference(start_date, end_date)
    else:
        months_difference = num_of_weeks_to_end_payment
    period = f"{months_difference} months"

    interest_rate_percentage_over_a_year = db.query(models.LoanAccount) \
        .join(models.MemberLoanAccount,
              models.MemberLoanAccount.loan_id == models.LoanAccount.id) \
        .join(models.LoansTransaction,
              models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()
    interest_rate_per_year = interest_rate_percentage_over_a_year.interest_amt
    interest_per_rate_month_percent = interest_rate_per_year / 12

    amount = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    price = amount.amount
    interest_rate_percentage_on_loan = interest_per_rate_month_percent * months_difference
    interest_rate_per_month_value = interest_per_rate_month_percent / 100
    interest_rate = interest_rate_per_month_value * months_difference

    interest = price * interest_rate
    db.commit()
    loan_advise = models.LoanAdvise(
        period=period,
        interest_rate_percentage=interest_rate_percentage_on_loan,
        interest_rate_amount=interest,
        repayment_starting_date=repayment_starts,
        repayment_ending_date=repayment_end_date,
        application_fee=app_fee,
        proccessing_fee=pro_fee,
        loan_transaction_id=transaction_id,
        issue_date=datetime.now()
    )
    db.add(loan_advise)
    db.commit()
    hj = round(price + interest, 2)

    if loanTransaction.balance:
        update_d = {
            models.LoansTransaction.balance: -(hj + loanTransaction.balance)
        }
    else:
        update_d = {
            models.LoansTransaction.balance: -hj
        }

    update = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .update(update_d)

    db.commit()

    balance_account.current_balance = -(balance_account.current_balance + hj)

    db.commit()

    updated_transaction = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    return "Loan Disbursed"


def calculate_duration(start_date: datetime, end_date: datetime, duration_type: str) -> Union[int, None]:
    if duration_type == "weeks":
        total_weeks = (end_date - start_date).days // 7
        return total_weeks + 1
    elif duration_type == "months":
        return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    else:
        return None


@router.get("/loan/advise/{transaction_id}")
async def get_info_to_prepare_loan_advise(transaction_id: int,
                                          user: dict = Depends(get_current_user),
                                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    loan_details = db.query(models.LoanAdvise) \
        .filter(models.LoanAdvise.loan_transaction_id == transaction_id) \
        .first()
    transaction_details = db.query(models.LoansTransaction) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    more_details = db.query(models.Members.firstname,
                            models.Members.lastname,
                            models.Members.middlename,
                            models.Members.address,
                            models.Members.nextOfKin,
                            models.AssociationMembers.association_members_id,
                            models.Association.association_name,
                            models.Association.cluster_office,
                            models.Association.community_name,
                            models.LoansTransaction.amount,
                            models.LoansTransaction.time,
                            models.LoansTransaction.transaction_date,
                            models.MemberLoanAccount.member_id,
                            models.LoanAccount.account_name,
                            models.LoanAccount.application_fee,
                            models.LoanAccount.proccessing_fee,
                            ) \
        .select_from(models.LoansTransaction) \
        .join(models.MemberLoanAccount,
              models.LoansTransaction.loans_acc_id == models.MemberLoanAccount.id) \
        .join(models.LoanAccount,
              models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
        .join(models.Members,
              models.Members.member_id == models.MemberLoanAccount.member_id) \
        .join(models.AssociationMembers,
              models.AssociationMembers.association_members_id == models.MemberLoanAccount.association_member_id) \
        .join(models.Association,
              models.Association.association_id == models.AssociationMembers.association_id) \
        .filter(models.LoansTransaction.transaction_id == transaction_id) \
        .first()

    # print(more_details)

    amount_to_be_paid = round(more_details.amount + loan_details.interest_rate_amount, 2)
    total_interest_to_be_paid = loan_details.interest_rate_amount
    date_to_start_repayment = loan_details.repayment_starting_date
    date_to_end_repayment = loan_details.repayment_ending_date

    start_date = datetime.strptime(date_to_start_repayment, '%Y-%m-%d')
    end_date = datetime.strptime(date_to_end_repayment, '%Y-%m-%d')
    total_days = (end_date - start_date).days
    if more_details.time == "weeks":
        total_weeks = (total_days + 6) // 7
        amount_per_week = round(amount_to_be_paid / total_weeks, 2)
        interest_per_week = round(total_interest_to_be_paid / total_weeks, 2)
        weekly_payments = []
        current_date = start_date
        for week in range(total_weeks):
            while current_date.weekday() != 4:
                current_date += timedelta(days=1)

            weekly_payments.append({
                "Date": current_date.strftime('%Y-%m-%d'),
                "Amount_to_be_Paid": amount_per_week,
                "Interest_Amount": interest_per_week
            })

            current_date += timedelta(days=1)

        total_amount_per_week = round(sum(payment["Amount_to_be_Paid"] for payment in weekly_payments), 2)
        total_interest_per_week = round(sum(payment["Interest_Amount"] for payment in weekly_payments), 2)
        return {
            "Loan_Details": loan_details,
            "More_Details": more_details,
            "Transaction_Details": transaction_details,
            "Repayment_Schedule": weekly_payments,
            "Amount_Total": total_amount_per_week,
            "Interest_Total": total_interest_per_week,
            "Total_Khraa": round(total_amount_per_week + total_interest_per_week, 2)
        }
    elif more_details.time == "months":
        total_months = calculate_duration(start_date=start_date, end_date=end_date, duration_type=more_details.time)
        amount_per_month = round(amount_to_be_paid / total_months, 2)
        interest_per_month = round(total_interest_to_be_paid / total_months, 2)
        monthly_payments = []
        current_date = start_date
        for month in range(total_months):
            while current_date.day != 1:
                current_date += timedelta(days=1)

            monthly_payments.append({
                "Date": current_date.strftime('%Y-%m-%d'),
                "Amount_to_be_Paid": amount_per_month,
                "Interest_Amount": interest_per_month
            })

            current_date = current_date + relativedelta(months=1)

        total_amount_per_month = round(sum(payment["Amount_to_be_Paid"] for payment in monthly_payments), 2)
        total_interest_per_month = round(sum(payment["Interest_Amount"] for payment in monthly_payments), 2)
        return {
            "Loan_Details": loan_details,
            "More_Details": more_details,
            "Transaction_Details": transaction_details,
            "Repayment_Schedule": monthly_payments,
            "Amount_Total": total_amount_per_month,
            "Interest_Total": total_interest_per_month,
            "Total_Khraa": round(total_amount_per_month + total_interest_per_month, 2)
        }
    else:
        pass


@router.post("/transaction/loan/member_loans_acc_id")
async def get_one_loan_accounts_transactions(member_loans_acc_id: int = Form(...),
                                             start_date: Optional[str] = Form(None),
                                             end_date: Optional[str] = Form(None),
                                             user: dict = Depends(get_current_user),
                                             db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    total_with = 0
    total_dep = 0

    if start_date is None:
        accounts_transaction = db.query(
            models.LoansTransaction.transaction_date,
            models.LoansTransaction.narration,
            models.Users.username,
            models.LoansTransaction.amount,
            models.TransactionType.transactiontype_name,
            models.LoansTransaction.transaction_id,
            models.LoansTransaction.status,
            models.LoansTransaction.balance
        ).select_from(models.LoansTransaction) \
            .join(models.TransactionType,
                  models.LoansTransaction.transactiontype_id == models.TransactionType.transactype_id) \
            .join(models.Users,
                  models.Users.id == models.LoansTransaction.prep_by) \
            .filter(models.LoansTransaction.loans_acc_id == member_loans_acc_id) \
            .order_by(desc(models.LoansTransaction.transaction_date)) \
            .all()

        for item in accounts_transaction:
            if item.transactiontype_name == "Deposit":
                total_dep += item.amount
            elif item.transactiontype_name == "Withdraw":
                total_with += item.amount

        return {
            "data": accounts_transaction,
            "total_dep": total_dep,
            "total_wit": total_with
        }
    else:
        accounts_transaction = db.query(
            models.LoansTransaction.transaction_date,
            models.LoansTransaction.narration,
            models.Users.username,
            models.LoansTransaction.amount,
            models.TransactionType.transactiontype_name,
            models.LoansTransaction.transaction_id,
            models.LoansTransaction.status,
            models.LoansTransaction.balance
        ).select_from(models.LoansTransaction) \
            .join(models.TransactionType,
                  models.LoansTransaction.transactiontype_id == models.TransactionType.transactype_id) \
            .join(models.Users,
                  models.Users.id == models.LoansTransaction.prep_by) \
            .filter(models.LoansTransaction.loans_acc_id == member_loans_acc_id,
                    func.date(models.LoansTransaction.transaction_date) >= start_date,
                    func.date(models.LoansTransaction.transaction_date) <= end_date) \
            .order_by(desc(models.LoansTransaction.transaction_date)) \
            .all()

        for item in accounts_transaction:
            if item.transactiontype_name == "Deposit":
                total_dep += item.amount
            elif item.transactiontype_name == "Withdraw":
                total_with += item.amount

        return {
            "data": accounts_transaction,
            "total_dep": total_dep,
            "total_wit": total_with
        }

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

    shareValue = db.query(models.ShareAccount) \
        .select_from(models.ShareAccount) \
        .join(models.MemberShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .filter(models.MemberShareAccount.id == transactShare.shares_acc_id) \
        .first()

    shareValuue = db.query(models.MemberShareAccount) \
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
    transactions_models.balance = shareValuue.current_balance + stamp

    db.add(transactions_models)
    db.flush()
    db.commit()

    balance_account_share = db.query(models.MemberShareAccount) \
        .filter(models.MemberShareAccount.id == transactShare.shares_acc_id) \
        .first()

    if not balance_account_share:
        raise HTTPException(status_code=404, detail="Balance account not found")

    balance_account_share.current_balance = stamp

    db.commit()
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime('%Y-%m-%d')
    start_date = datetime.strptime(formatted_date, '%Y-%m-%d')
    period = transactShare.period
    if period < 1:
        months = 12 * period
        ending_date = start_date + timedelta(days=31 * months)
    else:
        ending_date = start_date + timedelta(days=365 * int(period))
    ending_date = ending_date.strftime('%Y-%m-%d')

    # transaction id
    share_transaction_id = db.query(models.SharesTransaction) \
        .order_by(desc(models.SharesTransaction.transaction_id)) \
        .first()
    # period

    end_date = datetime.strptime(ending_date, '%Y-%m-%d')

    years_difference = (end_date.year - start_date.year)
    months_difference = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    # print(years_difference, months_difference)
    interestPercentagePerYear = db.query(models.ShareAccount) \
        .select_from(models.SharesTransaction) \
        .join(models.MemberShareAccount,
              models.SharesTransaction.shares_acc_id == models.MemberShareAccount.id) \
        .join(models.ShareAccount,
              models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .first()
    price = share_transaction_id.amount
    if years_difference == 1 and months_difference < 12 or years_difference == 0:
        # print("years_difference == 0 and months_difference < 12")
        months_difference = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        period = f"{months_difference} months"
        interest_rate_percent = (interestPercentagePerYear.interest_amt / 12) * months_difference
        interestRateValue = interest_rate_percent / 100
        # interest_rate_amount = interestRateValue * months_difference
        interest = price * interestRateValue
    elif years_difference == 1:
        # print("years_difference == 1")
        period = "1 year"
        interest_rate_percent = interestPercentagePerYear.interest_amt
        interestRateValue = interest_rate_percent / 100
        interest_rate_amount = interestRateValue * 1
        interest = price * interest_rate_amount
    else:
        # print("years_difference > 1")
        period = f"{years_difference} years"
        interest_rate_percent = (interestPercentagePerYear.interest_amt / 100) * years_difference
        # interestRateValue = interest_rate_percent / 100
        # interest_rate_amount = interestRateValue * years_difference
        interest = price * interest_rate_percent
    share_certificate = models.ShareCert(
        period=period,
        interest_rate_percentage=interest_rate_percent,
        interest_rate_amount=interest,
        starting_date=formatted_date,
        ending_date=ending_date,
        on_due_date=transactShare.on_due_date,
        spending_means=f"{transactShare.spending_means} {transactShare.account_name}",
        share_transaction_id=share_transaction_id.transaction_id
    )
    db.add(share_certificate)
    db.commit()

    return "Share Purchased"


class SharesTransactionWith(BaseModel):
    transactiontype_id: int
    Amount: float
    narration: Optional[str]
    shares_acc_id: int


@router.post("/transaction/share/wit")
async def create_transactions_shares_acc_withdrawal(transactShare: SharesTransactionWith,
                                                    user: dict = Depends(get_current_user),
                                                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    shareValue = db.query(models.ShareAccount) \
        .join(models.MemberShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .filter(models.MemberShareAccount.id == transactShare.shares_acc_id) \
        .first()

    shareValuue = db.query(models.MemberShareAccount) \
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
    transactions_models.balance = shareValuue.current_balance - stamp

    db.add(transactions_models)
    db.flush()
    db.commit()

    return "Share Withdrawn"


@router.get("/share/slip/{transaction_id}")
async def get_share_cert_info(transaction_id: int,
                              user: dict = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    member_info = db.query(models.Members.lastname,
                           models.Members.firstname,
                           models.Members.middlename,
                           models.Members.address,
                           models.Members.Town,
                           models.Members.phone,
                           models.Members.nextOfKin,
                           models.SharesTransaction.amount,
                           models.SharesTransaction.transaction_date,
                           models.ShareAccount.account_name,
                           models.ShareAccount.interest_amt,
                           models.MemberShareAccount.association_member_id,
                           models.Association.association_name,
                           models.Association.cluster_office,
                           models.Association.community_name) \
        .select_from(models.SharesTransaction) \
        .join(models.MemberShareAccount,
              models.MemberShareAccount.id == models.SharesTransaction.shares_acc_id) \
        .join(models.AssociationMembers,
              models.MemberShareAccount.association_member_id == models.AssociationMembers.association_members_id) \
        .join(models.Association,
              models.AssociationMembers.association_id == models.Association.association_id) \
        .join(models.Members,
              models.Members.member_id == models.MemberShareAccount.member_id) \
        .join(models.ShareAccount,
              models.ShareAccount.id == models.MemberShareAccount.share_id) \
        .filter(models.SharesTransaction.transaction_id == transaction_id) \
        .first()

    transaction_details = db.query(models.ShareCert.period,
                                   models.ShareCert.interest_rate_percentage,
                                   models.ShareCert.interest_rate_amount,
                                   models.ShareCert.spending_means,
                                   models.ShareCert.on_due_date,
                                   models.ShareCert.starting_date,
                                   models.ShareCert.ending_date) \
        .select_from(models.ShareCert) \
        .filter(models.ShareCert.share_transaction_id == transaction_id) \
        .first()

    return {"Basic_Info": member_info, "Transaction_Details": transaction_details}


@router.post("/transaction/share/member_shares_acc_id")
async def get_one_shares_account_transactions(member_shares_acc_id: int = Form(...),
                                              start_date: Optional[str] = Form(None),
                                              end_date: Optional[str] = Form(None),
                                              user: dict = Depends(get_current_user),
                                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    total_with = 0
    total_dep = 0

    if start_date is None:
        accounts_transaction = db.query(
            models.SharesTransaction.transaction_date,
            models.SharesTransaction.narration,
            models.Users.username,
            models.SharesTransaction.amount,
            models.TransactionType.transactiontype_name,
            models.SharesTransaction.transaction_id,
            models.SharesTransaction.balance
        ).select_from(models.SharesTransaction) \
            .join(models.TransactionType,
                  models.SharesTransaction.transactiontype_id == models.TransactionType.transactype_id) \
            .join(models.Users,
                  models.Users.id == models.SharesTransaction.prep_by) \
            .filter(models.SharesTransaction.shares_acc_id == member_shares_acc_id) \
            .order_by(desc(models.SharesTransaction.transaction_date)) \
            .all()

        for item in accounts_transaction:
            if item.transactiontype_name == "Deposit":
                total_dep += item.amount
            elif item.transactiontype_name == "Withdraw":
                total_with += item.amount

        return {
            "data": accounts_transaction,
            "total_dep": total_dep,
            "total_wit": total_with
        }
    else:
        accounts_transaction = db.query(
            models.SharesTransaction.transaction_date,
            models.SharesTransaction.narration,
            models.Users.username,
            models.SharesTransaction.amount,
            models.TransactionType.transactiontype_name,
            models.SharesTransaction.transaction_id,
            models.SharesTransaction.balance
        ).select_from(models.SharesTransaction) \
            .join(models.TransactionType,
                  models.SharesTransaction.transactiontype_id == models.TransactionType.transactype_id) \
            .join(models.Users,
                  models.Users.id == models.SharesTransaction.prep_by) \
            .filter(models.SharesTransaction.shares_acc_id == member_shares_acc_id,
                    func.date(models.SharesTransaction.transaction_date) >= start_date,
                    func.date(models.SharesTransaction.transaction_date) <= end_date) \
            .order_by(desc(models.SharesTransaction.transaction_date)) \
            .all()
        for item in accounts_transaction:
            if item.transactiontype_name == "Deposit":
                total_dep += item.amount
            elif item.transactiontype_name == "Withdraw":
                total_with += item.amount

        return {
            "data": accounts_transaction,
            "total_dep": total_dep,
            "total_wit": total_with
        }


@router.get("/savings/share/{member_shares_acc_id}")
async def get_one_shares_account_savings_account(member_shares_acc_id: int,
                                                 user: dict = Depends(get_current_user),
                                                 db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    accountss = db.query(models.SavingsAccount.account_name,
                         models.MemberSavingsAccount.id) \
        .select_from(models.MemberShareAccount) \
        .join(models.Members,
              models.Members.member_id == models.MemberShareAccount.member_id) \
        .join(models.MemberSavingsAccount,
              models.MemberSavingsAccount.member_id == models.Members.member_id) \
        .join(models.SavingsAccount,
              models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
        .filter(models.MemberShareAccount.id == member_shares_acc_id) \
        .all()
    return {"Accounts": accountss}


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
    period: Optional[float]
    on_due_date: Optional[str]
    spending_means: Optional[str]
    account_name: Optional[str]


@router.post("/transfer")
async def transfers_in_savings_account(tranfer: TransferSavings,
                                       user: dict = Depends(get_current_user),
                                       db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    if tranfer.to_accountType == "savings":
        to_acc = db.query(models.Members.firstname,
                          models.Members.lastname,
                          models.SavingsAccount.account_name,
                          models.MemberSavingsAccount.current_balance) \
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
            transfer_from.balance = from_acc.current_balance - tranfer.Amount
            transfer_from.transaction_date = datetime.now()
            transfer_from.prep_by = user.get("id")
            db.add(transfer_from)
            db.commit()

            trn = models.SavingsTransaction()
            trn.transactiontype_id = 1
            trn.amount = tranfer.Amount
            trn.narration = f"Received from: {from_acc.firstname} {from_acc.lastname}'s {from_acc.account_name} account"
            trn.savings_acc_id = tranfer.to_member_account_id
            trn.balance = to_acc.current_balance + tranfer.Amount
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
                          models.LoanAccount.account_name,
                          models.MemberLoanAccount.current_balance) \
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
            transfer_from.balance = from_acc.current_balance - tranfer.Amount
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
            trn_to.balance = to_acc.current_balance + tranfer.Amount
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
                          models.ShareAccount.account_name,
                          models.MemberShareAccount.current_balance) \
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
        share_value = await get_share_value(member_shares_acc_id=tranfer.to_member_account_id,
                                      user=user,
                                      db=db)

        transfer_from = models.SavingsTransaction()
        transfer_from.amount = tranfer.Amount * share_value.share_value
        transfer_from.narration = f"Transferred to: {to_acc.firstname} {to_acc.lastname}'s {to_acc.account_name} account"
        transfer_from.savings_acc_id = tranfer.savings_acc_id
        transfer_from.transactiontype_id = 2
        transfer_from.balance = from_acc.current_balance - tranfer.Amount
        transfer_from.transaction_date = datetime.now()
        transfer_from.prep_by = user.get("id")
        db.add(transfer_from)
        db.commit()

        riri = SharesTransaction(
            transactiontype_id=1,
            Amount=tranfer.Amount,
            narration=f"Purchased from: {from_acc.firstname} {from_acc.lastname}'s {from_acc.account_name} account",
            shares_acc_id=tranfer.to_member_account_id,
            period=tranfer.period,
            on_due_date=tranfer.on_due_date,
            spending_means=tranfer.spending_means,
            account_name=tranfer.account_name
        )

        await create_transactions_shares_acc(
            transactShare=riri,
            user=user,
            db=db
        )

        return f"Transfer Complete"
    else:
        raise insufficient_balance()


class Info_All(BaseModel):
    member_id: int
    account_name: Optional[str]
    type: Optional[str]


@router.post("/transfer/info")
async def get_info_for_transfer(data: Info_All,
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
        .filter(models.MemberSavingsAccount.member_id != data.member_id) \
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
        .filter(models.MemberSavingsAccount.member_id != data.member_id) \
        .all()
    if data.account_name and data.type == "filter_my_savings":
        my_savings = db.query(models.MemberSavingsAccount.id,
                              models.Association.association_name,
                              models.SavingsAccount.account_name) \
            .select_from(models.MemberSavingsAccount) \
            .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
            .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
            .join(models.AssociationMembers,
                  models.AssociationMembers.association_members_id == models.MemberSavingsAccount.association_member_id) \
            .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
            .filter(models.MemberSavingsAccount.member_id == data.member_id) \
            .filter(models.SavingsAccount.account_name.like(f"%{data.account_name}%")) \
            .all()
    else:
        my_savings = db.query(models.MemberSavingsAccount.id,
                              models.Association.association_name,
                              models.SavingsAccount.account_name) \
            .select_from(models.MemberSavingsAccount) \
            .join(models.Members, models.Members.member_id == models.MemberSavingsAccount.member_id) \
            .join(models.SavingsAccount, models.SavingsAccount.id == models.MemberSavingsAccount.savings_id) \
            .join(models.AssociationMembers,
                  models.AssociationMembers.association_members_id == models.MemberSavingsAccount.association_member_id) \
            .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
            .filter(models.MemberSavingsAccount.member_id == data.member_id) \
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
        .filter(models.MemberLoanAccount.member_id != data.member_id) \
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
        .filter(models.MemberLoanAccount.member_id != data.member_id) \
        .all()
    if data.account_name and data.type == "filter_my_loans":
        my_loans = db.query(models.MemberLoanAccount.id,
                            models.Association.association_name,
                            models.LoanAccount.account_name) \
            .select_from(models.MemberLoanAccount) \
            .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
            .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
            .join(models.AssociationMembers,
                  models.AssociationMembers.association_members_id == models.MemberLoanAccount.association_member_id) \
            .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
            .filter(models.MemberLoanAccount.member_id == data.member_id,
                    models.LoanAccount.account_name.like(f"%{data.account_name}%")) \
            .all()
    else:
        my_loans = db.query(models.MemberLoanAccount.id,
                            models.Association.association_name,
                            models.LoanAccount.account_name) \
            .select_from(models.MemberLoanAccount) \
            .join(models.Members, models.Members.member_id == models.MemberLoanAccount.member_id) \
            .join(models.LoanAccount, models.LoanAccount.id == models.MemberLoanAccount.loan_id) \
            .join(models.AssociationMembers,
                  models.AssociationMembers.association_members_id == models.MemberLoanAccount.association_member_id) \
            .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
            .filter(models.MemberLoanAccount.member_id == data.member_id) \
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
        .filter(models.MemberShareAccount.member_id != data.member_id) \
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
        .filter(models.MemberShareAccount.member_id != data.member_id) \
        .all()
    if data.account_name and data.type == "filter_my_share":
        my_shares = db.query(models.MemberShareAccount.id,
                             models.Association.association_name,
                             models.ShareAccount.account_name) \
            .select_from(models.MemberShareAccount) \
            .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
            .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
            .join(models.AssociationMembers,
                  models.AssociationMembers.association_members_id == models.MemberShareAccount.association_member_id) \
            .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
            .filter(models.MemberShareAccount.member_id == data.member_id,
                    models.ShareAccount.account_name.like(f"%{data.account_name}%")) \
            .all()
    else:
        my_shares = db.query(models.MemberShareAccount.id,
                             models.Association.association_name,
                             models.ShareAccount.account_name) \
            .select_from(models.MemberShareAccount) \
            .join(models.Members, models.Members.member_id == models.MemberShareAccount.member_id) \
            .join(models.ShareAccount, models.ShareAccount.id == models.MemberShareAccount.share_id) \
            .join(models.AssociationMembers,
                  models.AssociationMembers.association_members_id == models.MemberShareAccount.association_member_id) \
            .join(models.Association, models.Association.association_id == models.AssociationMembers.association_id) \
            .filter(models.MemberShareAccount.member_id == data.member_id) \
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
