import base64
import sys

sys.path.append("../..")

from fastapi import Depends, HTTPException, APIRouter, File, UploadFile, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from .auth import get_current_user, get_user_exception, get_password_hash, verify_password

router = APIRouter(
    prefix="/permissions",
    tags=["permissions"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class NewPermissions(BaseModel):
    role_id: int
    create_member: Optional[bool]
    update_member: Optional[bool]
    delete_member: Optional[bool]
    view_member: Optional[bool]
    create_association: Optional[bool]
    update_association: Optional[bool]
    view_association: Optional[bool]
    delete_association: Optional[bool]
    create_society: Optional[bool]
    update_society: Optional[bool]
    view_society: Optional[bool]
    delete_society: Optional[bool]
    create_association_type: Optional[bool]
    update_association_type: Optional[bool]
    view_association_type: Optional[bool]
    delete_association_type: Optional[bool]
    create_savings_transactions: Optional[bool]
    update_savings_transactions: Optional[bool]
    view_savings_transactions: Optional[bool]
    delete_savings_transactions: Optional[bool]
    request_loan_transactions: Optional[bool]
    update_loan_request: Optional[bool]
    view_loan_transactions: Optional[bool]
    delete_loan_transactions: Optional[bool]
    download_loan_advise: Optional[bool]
    approve_loan_requests: Optional[bool]
    disburse_approved_loans: Optional[bool]
    create_shares_transactions: Optional[bool]
    view_share_transactions: Optional[bool]
    download_share_cert: Optional[bool]
    delete_share_transactions: Optional[bool]
    view_association_passbook: Optional[bool]
    view_association_momo_account: Optional[bool]
    set_association_momo_bal: Optional[bool]
    view_society_account: Optional[bool]
    view_society_reconciliatio_form: Optional[bool]
    reconcile_balances: Optional[bool]
    view_bank_accounts: Optional[bool]
    create_bank_accounts: Optional[bool]
    create_bank_transactions: Optional[bool]
    view_bank_transactions: Optional[bool]
    update_bank_transactions: Optional[bool]
    delete_bank_transactions: Optional[bool]
    create_savings_account: Optional[bool]
    update_savings_account: Optional[bool]
    delete_savings_account: Optional[bool]
    create_loan_account: Optional[bool]
    update_loan_account: Optional[bool]
    delete_loan_account: Optional[bool]
    create_share_account: Optional[bool]
    update_share_account: Optional[bool]
    delete_share_account: Optional[bool]
    create_warehouse: Optional[bool]
    create_commodity: Optional[bool]
    view_savings_account: Optional[bool]
    view_loans_account: Optional[bool]
    view_shares_account: Optional[bool]
    view_commodity_account: Optional[bool]
    view_warehouse: Optional[bool]


@router.post("/set")
async def set_permissions(new_rules: NewPermissions,
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    update_data = {
        models.UserRoles.create_member: new_rules.create_member,
        models.UserRoles.update_member: new_rules.update_member,
        models.UserRoles.delete_member: new_rules.delete_member,
        models.UserRoles.view_member: new_rules.view_member,
        models.UserRoles.create_association: new_rules.create_association,
        models.UserRoles.update_association: new_rules.update_association,
        models.UserRoles.view_association: new_rules.view_association,
        models.UserRoles.delete_association: new_rules.delete_association,
        models.UserRoles.create_society: new_rules.create_society,
        models.UserRoles.update_society: new_rules.create_society,
        models.UserRoles.view_society: new_rules.view_society,
        models.UserRoles.delete_society: new_rules.delete_society,
        models.UserRoles.create_association_type: new_rules.create_association_type,
        models.UserRoles.update_association_type: new_rules.update_association_type,
        models.UserRoles.view_association_type: new_rules.view_association_type,
        models.UserRoles.delete_association_type: new_rules.delete_association_type,
        models.UserRoles.create_savings_transactions: new_rules.create_savings_transactions,
        models.UserRoles.update_savings_transactions: new_rules.update_savings_transactions,
        models.UserRoles.view_savings_transactions: new_rules.view_savings_transactions,
        models.UserRoles.delete_savings_transactions: new_rules.delete_savings_transactions,
        models.UserRoles.request_loan_transactions: new_rules.request_loan_transactions,
        models.UserRoles.update_loan_request: new_rules.update_loan_request,
        models.UserRoles.view_loan_transactions: new_rules.view_loan_transactions,
        models.UserRoles.delete_loan_transactions: new_rules.delete_loan_transactions,
        models.UserRoles.download_loan_advise: new_rules.download_loan_advise,
        models.UserRoles.approve_loan_requests: new_rules.approve_loan_requests,
        models.UserRoles.disburse_approved_loans: new_rules.disburse_approved_loans,
        models.UserRoles.create_shares_transactions: new_rules.create_shares_transactions,
        models.UserRoles.view_share_transactions: new_rules.view_share_transactions,
        models.UserRoles.download_share_cert: new_rules.download_share_cert,
        models.UserRoles.delete_share_transactions: new_rules.delete_share_transactions,
        models.UserRoles.view_association_passbook: new_rules.view_association_passbook,
        models.UserRoles.view_association_momo_account: new_rules.view_association_momo_account,
        models.UserRoles.set_association_momo_bal: new_rules.set_association_momo_bal,
        models.UserRoles.view_society_account: new_rules.view_society_account,
        models.UserRoles.view_society_reconciliatio_form: new_rules.view_society_reconciliatio_form,
        models.UserRoles.reconcile_balances: new_rules.reconcile_balances,
        models.UserRoles.view_bank_accounts: new_rules.view_bank_accounts,
        models.UserRoles.create_bank_accounts: new_rules.create_bank_accounts,
        models.UserRoles.create_bank_transactions: new_rules.create_bank_transactions,
        models.UserRoles.view_bank_transactions: new_rules.view_bank_transactions,
        models.UserRoles.update_bank_transactions: new_rules.update_bank_transactions,
        models.UserRoles.delete_bank_transactions: new_rules.delete_bank_transactions,
        models.UserRoles.create_savings_account: new_rules.create_savings_account,
        models.UserRoles.update_savings_account: new_rules.update_savings_account,
        models.UserRoles.delete_savings_account: new_rules.delete_savings_account,
        models.UserRoles.create_loan_account: new_rules.create_loan_account,
        models.UserRoles.update_loan_account: new_rules.update_loan_account,
        models.UserRoles.delete_loan_account: new_rules.delete_loan_account,
        models.UserRoles.create_share_account: new_rules.create_share_account,
        models.UserRoles.update_share_account: new_rules.update_share_account,
        models.UserRoles.delete_share_account: new_rules.delete_share_account,
        models.UserRoles.create_warehouse: new_rules.create_warehouse,
        models.UserRoles.create_commodity: new_rules.create_commodity,
        models.UserRoles.view_savings_account: new_rules.view_savings_account,
        models.UserRoles.view_loans_account: new_rules.view_loans_account,
        models.UserRoles.view_shares_account: new_rules.view_shares_account,
        models.UserRoles.view_commodity_account: new_rules.view_commodity_account,
        models.UserRoles.view_warehouse: new_rules.view_warehouse,
    }

    old_data = db.query(models.UserRoles).filter(models.UserRoles.id == new_rules.role_id).update(update_data)
    db.commit()

    return "Permissions Updated"


@router.get("/{role_id}")
async def get_permissions(role_id: int,
                          user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    all = db.query(models.UserRoles).filter(models.UserRoles.id == role_id).all()
    return {"Data": all}
