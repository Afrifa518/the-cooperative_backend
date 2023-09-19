import sys

from sqlalchemy import desc, func

sys.path.append("../..")

from typing import Optional, List
from fastapi import Depends, HTTPException, APIRouter
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
    calc_means: str
    commodities: Optional[List[str]] = None,
    value: float
    community: str


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
    commodity_model.calc_means = commodity.calc_means
    commodity_model.value = commodity.value
    commodity_model.community = commodity.community

    db.add(commodity_model)
    db.flush()
    db.commit()

    add_commodities(commodities=commodity.commodities, db=db)

    return "Setup Complete"


def add_commodities(commodities: Optional[List[str]] = None,
                    db: Session = Depends(get_db)):
    commodity_account = db.query(models.CommodityAccount) \
        .order_by(desc(models.CommodityAccount.id)) \
        .first()

    if not commodity_account:
        raise HTTPException(status_code=404, detail="Commodity account not found")

    try:
        if commodities:
            commodity_models = []
            for commodity in commodities:
                commo_model = models.Commodities(
                    commodity_acc_id=commodity_account.id,
                    commodities=commodity
                )
                commodity_models.append(commo_model)
            db.bulk_save_objects(commodity_models)
            db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Commodity creation failed")

    return "Success"


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
    member_account.amt_of_commodities = 0
    member_account.amt_valued = 0.00
    member_account.association_member_id = acc.association_member_id
    member_account.member_id = acc.member_id

    db.add(member_account)
    db.commit()

    return "New Account Activated"


@router.get("/commodity/")
async def get_commodities(user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    all_commodities = db.query(
        models.CommodityAccount.id.label('account_id'),
        func.count(models.Commodities.id).label('commodity_count'),
        models.CommodityAccount.warehouse,
        models.CommodityAccount.value,
        models.CommodityAccount.community,
        models.CommodityAccount.calc_means
    ).outerjoin(
        models.Commodities,
        models.CommodityAccount.id == models.Commodities.commodity_acc_id,
    ).group_by(
        models.CommodityAccount.id,
        models.CommodityAccount.warehouse,
        models.CommodityAccount.calc_means,
        models.CommodityAccount.value,
        models.CommodityAccount.community,
    ).all()

    return all_commodities


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
            models.MemberCommodityAccount.amt_of_commodities,
            models.MemberCommodityAccount.open_date,
            models.MemberCommodityAccount.amt_valued,
            models.CommodityAccount.warehouse,
            models.CommodityAccount.value
        )
        .select_from(models.MemberCommodityAccount)
        .join(models.CommodityAccount, models.MemberCommodityAccount.commodity_id == models.CommodityAccount.id)
        .filter(models.MemberCommodityAccount.member_id == member_id)
        .all()
    )

    for commodityrow in all_commodity_accounts:
        (
            id,
            amt_of_commodities,
            open_date,
            amt_valued,
            warehouse,
            value,
        ) = commodityrow
        all_commodities = (
            db.query(
                models.CommodityAccount.id,
                models.Commodities.commodities
            ).select_from(models.CommodityAccount)
            .join(models.Commodities, models.CommodityAccount.id == models.Commodities.commodity_acc_id)
            .filter(models.CommodityAccount.id == commodityrow.id)
            .all()
        )
        commodities_list = [
            {
                "Commodity_Names": c.commodities
            } for c in all_commodities
        ]
        commodity.append({
            "ID": id,
            "Amt_of_Commodity": amt_of_commodities,
            "open_date": open_date,
            "Amount_value": amt_valued,
            "Warehouse_name": warehouse,
            "Overall_value": value,
            "Commodity_Names": commodities_list,
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
            models.MemberSavingsAccount.open_date,
            models.MemberSavingsAccount.id,
            models.MemberSavingsAccount.current_balance,
            models.SavingsAccount.account_name,
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
        .filter(models.MemberLoanAccount.association_member_id == association_member_id)
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
        .filter(models.MemberShareAccount.association_member_id == association_member_id)
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
            models.MemberCommodityAccount.amt_of_commodities,
            models.MemberCommodityAccount.open_date,
            models.MemberCommodityAccount.amt_valued,
            models.CommodityAccount.warehouse,
            models.CommodityAccount.value
        )
        .select_from(models.MemberCommodityAccount)
        .join(models.CommodityAccount, models.MemberCommodityAccount.commodity_id == models.CommodityAccount.id)
        .filter(models.MemberCommodityAccount.association_member_id == association_member_id)
        .all()
    )

    for commodityrow in all_commodity_accounts:
        (
            id,
            amt_of_commodities,
            open_date,
            amt_valued,
            warehouse,
            value,
        ) = commodityrow
        all_commodities = (
            db.query(
                models.CommodityAccount.id,
                models.Commodities.commodities
            ).select_from(models.CommodityAccount)
            .join(models.Commodities, models.CommodityAccount.id == models.Commodities.commodity_acc_id)
            .filter(models.CommodityAccount.id == commodityrow.id)
            .all()
        )
        commodities_list = [
            {
                "Commodity_Names": c.commodities
            } for c in all_commodities
        ]
        commodity.append({
            "ID": id,
            "Amt_of_Commodity": amt_of_commodities,
            "open_date": open_date,
            "Amount_value": amt_valued,
            "Warehouse_name": warehouse,
            "Overall_value": value,
            "Commodity_Names": commodities_list,
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
        ).filter(models.MemberLoanAccount.id == loans_account_id).first()
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
async def get_loan_info(commodity_account_id: int,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    data_nkoa = (
        db.query(
            models.MemberCommodityAccount.id,
            models.MemberCommodityAccount.open_date,
            models.MemberCommodityAccount.amt_of_commodities,
            models.MemberCommodityAccount.amt_valued,
        ).filter(models.MemberCommodityAccount.id == commodity_account_id).first()
    )
    timestamp = f"{data_nkoa.open_date}"
    datetime_obj = datetime.fromisoformat(timestamp)
    formatted_date = datetime_obj.strftime("%Y-%m-%d %H-%M-%S")
    data_nkoa_json = [
        {
            "id": data_nkoa.id,
            "open_date": formatted_date,
            "amount_of_commodities": data_nkoa.amt_of_commodities,
            "amount_valued": data_nkoa.amt_valued
        }
    ]

    if not data_nkoa_json:
        return {}

    return data_nkoa_json
