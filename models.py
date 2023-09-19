from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, UniqueConstraint
from sqlalchemy.dialects.postgresql import (
    BOOLEAN, TIMESTAMP,
    TEXT, VARCHAR, DATE, FLOAT
)
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String)
    firstName = Column(String)
    middleName = Column(String)
    lastName = Column(String)
    email = Column(String)
    hashed_password = Column(String)

    savings_transactions = relationship("SavingsTransaction", back_populates="prepared_by")
    loans_transactions = relationship("LoansTransaction", back_populates="prepared_by")
    shares_transactions = relationship("SharesTransaction", back_populates="prepared_by")
    info = relationship("UserInfo", back_populates="user")
    user_staff = relationship("Association", foreign_keys="Association.staff_userid", back_populates="staff_user")
    user_creator = relationship("Association", foreign_keys="Association.created_by", back_populates="creator")


class UserInfo(Base):
    __tablename__ = "user_info"

    userInfo_id = Column(Integer, primary_key=True, index=True)
    dob = Column(DATE)
    gender = Column(String)
    address = Column(String)
    phone = Column(String)
    userImage = Column(TEXT)
    users_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="info")


class Members(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    middlename = Column(String)
    lastname = Column(String)
    dob = Column(DATE)
    gender = Column(String)
    phone = Column(String)
    otherPhone = Column(String)
    address = Column(String)
    otherAddress = Column(String)
    ghcardnumber = Column(String, unique=True)
    ghCardImage = Column(LargeBinary)
    memberImage = Column(LargeBinary)
    nextOfKin = Column(String)
    otherName = Column(String)
    commonname = Column(String)
    MaritalStatus = Column(String)
    EducationLevel = Column(String)
    Town = Column(String)
    ruralOrUrban = Column(String)

    __table_args__ = (
        UniqueConstraint('ghcardnumber', name='card_number_unique'),
    )

    meaccount = relationship("MemberShareAccount", back_populates="meid")
    member_members = relationship("MemberLoanAccount", back_populates="membersowwn")
    member_member = relationship("MemberCommodityAccount", back_populates="membersown")
    leadus = relationship("AssociationLeaders", back_populates="lead")
    association = relationship("AssociationMembers", back_populates="assomem")
    thankyou = relationship("MemberSavingsAccount", back_populates="youhavemoney")

class SavingsAccount(Base):
    __tablename__ = "savings_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    is_refundable = Column(BOOLEAN)
    medium_of_exchange = Column(String)
    interest_over_a_year = Column(FLOAT)
    stamp_value = Column(FLOAT)

    okihr = relationship("MemberSavingsAccount", back_populates="save")


class LoanAccount(Base):
    __tablename__ = "loan_account"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    interest_amt = Column(FLOAT)
    application_fee = Column(FLOAT)
    proccessing_fee = Column(FLOAT)
    min_amt = Column(FLOAT)
    max_amt = Column(FLOAT)

    member_loan = relationship("MemberLoanAccount", back_populates="loan")


class ShareAccount(Base):
    __tablename__ = "share_account"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    share_value = Column(FLOAT)
    interest_amt = Column(FLOAT)

    shareme = relationship("MemberShareAccount", back_populates="share")


class CommodityAccount(Base):
    __tablename__ = "commodity_account"

    id = Column(Integer, primary_key=True, index=True)
    warehouse = Column(String)
    calc_means = Column(String)
    value = Column(FLOAT)
    community = Column(String)

    commo = relationship("Commodities", back_populates="dities")
    member_commodity = relationship("MemberCommodityAccount", back_populates="commodity")

class Commodities(Base):
    __tablename__ = 'commodities'

    id = Column(Integer, primary_key=True, index=True)
    commodities = Column(String)
    commodity_acc_id = Column(Integer, ForeignKey("commodity_account.id"))

    dities = relationship("CommodityAccount", back_populates="commo")
class MemberSavingsAccount(Base):
    __tablename__ = "member_savings_acc"

    id = Column(Integer, primary_key=True, index=True)
    savings_id = Column(Integer, ForeignKey("savings_accounts.id"))
    open_date = Column(TIMESTAMP)
    current_balance = Column(FLOAT)
    association_member_id = Column(Integer, ForeignKey("associationmembers.association_members_id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))

    savings_transactions = relationship("SavingsTransaction", back_populates="savings_account")
    save = relationship("SavingsAccount", back_populates="okihr")
    passsave = relationship("AssociationMembers", back_populates="okiwill")
    youhavemoney = relationship("Members", back_populates="thankyou")


class MemberShareAccount(Base):
    __tablename__ = "member_share_acc"

    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(Integer, ForeignKey("share_account.id"))
    open_date = Column(TIMESTAMP)
    current_balance = Column(FLOAT)
    association_member_id = Column(Integer, ForeignKey("associationmembers.association_members_id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))

    shares_transactions = relationship("SharesTransaction", back_populates="shares_accounts")
    share = relationship("ShareAccount", back_populates="shareme")
    memss = relationship("AssociationMembers", back_populates="money")
    meid = relationship("Members", back_populates="meaccount")


class MemberLoanAccount(Base):
    __tablename__ = "member_loan_acc"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loan_account.id"))
    open_date = Column(TIMESTAMP)
    current_balance = Column(FLOAT)
    association_member_id = Column(Integer, ForeignKey("associationmembers.association_members_id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))

    loans_transactions = relationship("LoansTransaction", back_populates="loan_account")
    loan = relationship("LoanAccount", back_populates="member_loan")
    membersowwn = relationship("Members", back_populates="member_members")
    passbookk = relationship("AssociationMembers", back_populates="passingg")


class MemberCommodityAccount(Base):
    __tablename__ = "member_commodity_acc"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodity_account.id"))
    open_date = Column(TIMESTAMP)
    amt_of_commodities = Column(Integer)
    amt_valued = Column(FLOAT)
    association_member_id = Column(Integer, ForeignKey("associationmembers.association_members_id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))

    commodity = relationship("CommodityAccount", back_populates="member_commodity")
    membersown = relationship("Members", back_populates="member_member")
    passbook = relationship("AssociationMembers", back_populates="passing")




class AssociationType(Base):
    __tablename__ = "associationtype"

    associationtype_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    association_type = Column(String)
    accepted_forms = Column(String)
    open_date = Column(TIMESTAMP)

    asso = relationship("Association", back_populates="assotype")


class Association(Base):
    __tablename__ = "association"

    association_id = Column(Integer, primary_key=True, index=True)
    association_name = Column(VARCHAR, nullable=False)
    association_type_id = Column(VARCHAR, ForeignKey("associationtype.associationtype_id"))
    community_name = Column(TEXT)
    open_date = Column(DATE)
    facilitator_userid = Column(Integer, ForeignKey("users.id"))
    association_email = Column(String)
    cluster_office = Column(String)
    staff_userid = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    staff_user = relationship("Users", foreign_keys="[Association.staff_userid]", back_populates="user_staff")
    creator = relationship("Users", foreign_keys="[Association.created_by]", back_populates="user_creator")
    members = relationship("AssociationMembers", back_populates="memasso")
    assotype = relationship("AssociationType", back_populates="asso")
    leader = relationship("AssociationLeaders", back_populates="associa")


class AssociationLeaders(Base):
    __tablename__ = "AssociationLeaders"

    leader_id = Column(Integer, primary_key=True, index=True)
    association_id = Column(Integer, ForeignKey("association.association_id"))
    member1_id = Column(Integer, ForeignKey("members.member_id"))

    lead = relationship("Members", back_populates="leadus")
    associa = relationship("Association", back_populates="leader")


class AssociationMembers(Base):
    __tablename__ = "associationmembers"

    association_members_id = Column(Integer, primary_key=True, index=True)
    association_id = Column(Integer, ForeignKey("association.association_id"))
    members_id = Column(Integer, ForeignKey("members.member_id"))

    assomem = relationship("Members", back_populates="association")
    memasso = relationship("Association", back_populates="members")
    passing = relationship("MemberCommodityAccount", back_populates="passbook")
    passingg = relationship("MemberLoanAccount", back_populates="passbookk")
    money = relationship("MemberShareAccount", back_populates="memss")
    okiwill = relationship("MemberSavingsAccount", back_populates="passsave")

class TransactionType(Base):
    __tablename__ = "transaction_type"

    transactype_id = Column(Integer, primary_key=True, index=True)
    transactiontype_name = Column(VARCHAR)

    savings_transactions = relationship("SavingsTransaction", back_populates="transaction_type")
    loantransact = relationship("LoansTransaction", back_populates="transaction_type")
    sharetransact = relationship("SharesTransaction", back_populates="transaction_type")


class SavingsTransaction(Base):
    __tablename__ = "savings_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transactiontype_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(FLOAT)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(TIMESTAMP)
    savings_acc_id = Column(Integer, ForeignKey("member_savings_acc.id"))


    savings_account = relationship("MemberSavingsAccount", back_populates="savings_transactions")
    transaction_type = relationship("TransactionType", back_populates="savings_transactions")
    prepared_by = relationship("Users", back_populates="savings_transactions")


class LoansTransaction(Base):
    __tablename__ = "loans_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transactiontype_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(FLOAT)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(TIMESTAMP)
    loans_acc_id = Column(Integer, ForeignKey("member_loan_acc.id"))
    status = Column(String)

    loan_account = relationship("MemberLoanAccount", back_populates="loans_transactions")
    transaction_type = relationship("TransactionType", back_populates="loantransact")
    prepared_by = relationship("Users", back_populates="loans_transactions")

class SharesTransaction(Base):
    __tablename__ = "shares_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transactiontype_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(FLOAT)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(TIMESTAMP)
    shares_acc_id = Column(Integer, ForeignKey("member_share_acc.id"))

    shares_accounts = relationship("MemberShareAccount", back_populates="shares_transactions")
    transaction_type = relationship("TransactionType", back_populates="sharetransact")
    prepared_by = relationship("Users", back_populates="shares_transactions")
