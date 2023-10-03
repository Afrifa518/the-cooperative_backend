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
    nu_nipa = relationship("CommodityTransactions", back_populates="nipa_nu")


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


class Commodities(Base):
    __tablename__ = 'commodities'

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String)

    tracked = relationship("CommodityValueTrack", back_populates="tracker")
    thingsthe = relationship("CommodityTransactions", back_populates="thethings")
    ankasa_com = relationship("MemberCommodityAccCommodities", back_populates="com_ankasa")
    type_commodity = relationship("AssociationTypeCommodities", back_populates="commodity_type")
    redarg = relationship("CommodityGradeValues", back_populates="grader")
    ytidommoc = relationship("CommodityUnitsJoin", back_populates="commodity")
    commod = relationship("CommodityAccountCommodities", back_populates="accommo")


class UnitsKg(Base):
    __tablename__ = "units/kg"

    id = Column(Integer, primary_key=True, index=True)
    unit_per_kg = Column("units/kg", Integer)

    trillion_per_unit = relationship("CommodityUnitsJoin", back_populates="unit_per_trillion")
    tinu = relationship("MemberCommodityAccCommodities", back_populates="unit")


class CommodityUnitsJoin(Base):
    __tablename__ = "commodity_units_join"

    commodity_units_join_id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"))
    unit_per_kg_id = Column("units/kg_id", Integer, ForeignKey("units/kg.id"))

    commodity = relationship("Commodities", back_populates="ytidommoc")
    unit_per_trillion = relationship("UnitsKg", back_populates="trillion_per_unit")


class CommodityGradeValues(Base):
    __tablename__ = "commodity_grade_values"

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(String)
    price_per_kg = Column("price/kg", FLOAT)
    commodities_id = Column(Integer, ForeignKey("commodities.id"))

    grader = relationship("Commodities", back_populates="redarg")


class CommodityAccount(Base):
    __tablename__ = "commodity_account"

    id = Column(Integer, primary_key=True, index=True)
    warehouse = Column(String)
    community = Column(String)
    association_type_id = Column(Integer, ForeignKey("associationtype.associationtype_id"))
    rebagging_fee = Column(FLOAT)
    treatment_fee = Column(FLOAT)
    destoning_fee = Column(FLOAT)
    cleaning_fee = Column(FLOAT)
    storage_fee = Column(FLOAT)
    tax_fee = Column(FLOAT)

    assohouse = relationship("AssociationType", back_populates="watertank")
    member_commodity = relationship("MemberCommodityAccount", back_populates="commodity")
    tnuota = relationship("CommodityAccountCommodities", back_populates="account")


class CommodityAccountCommodities(Base):
    __tablename__ = "commodity_account_commodities"

    account_commodities_id = Column(Integer, primary_key=True, index=True)
    commodity_account_id = Column(Integer, ForeignKey("commodity_account.id"))
    commodities_id = Column(Integer, ForeignKey("commodities.id"))

    account = relationship("CommodityAccount", back_populates="tnuota")
    accommo = relationship("Commodities", back_populates="commod")


class CommodityValueTrack(Base):
    __tablename__ = 'commodity_value_track'
    id = Column(Integer, primary_key=True, index=True)
    commodities_id = Column(Integer, ForeignKey("commodities.id"))
    date = Column(TIMESTAMP)
    new_price_per_kg = Column(FLOAT)
    grade = Column(String)
    new_units_per_kg = Column("new_units/kg", Integer)

    tracker = relationship("Commodities", back_populates="tracked")


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
    open_date = Column(TIMESTAMP)
    cash_value = Column(FLOAT)
    association_member_id = Column(Integer, ForeignKey("associationmembers.association_members_id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))
    commodity_id = Column(Integer, ForeignKey("commodity_account.id"))

    commodity = relationship("CommodityAccount", back_populates="member_commodity")
    membersown = relationship("Members", back_populates="member_member")
    passbook = relationship("AssociationMembers", back_populates="passing")
    nso_account = relationship("CommodityTransactions", back_populates="account_nso")
    things_acc = relationship("MemberCommodityAccCommodities", back_populates="acc_things")


class MemberCommodityAccCommodities(Base):
    __tablename__ = "member_commodity_acc_commodities"

    member_commodity_acc_commodities_id = Column(Integer, primary_key=True, index=True)
    member_acc_id = Column(Integer, ForeignKey("member_commodity_acc.id"))
    commodities_id = Column(Integer, ForeignKey("commodities.id"))
    units_id = Column(Integer, ForeignKey("units/kg.id"))
    total_number = Column(Integer)
    commodity_cash_value = Column(FLOAT)
    wieght = Column(Integer)
    tons = Column(Integer)

    acc_things = relationship("MemberCommodityAccount", back_populates="things_acc")
    com_ankasa = relationship("Commodities", back_populates="ankasa_com")
    unit = relationship("UnitsKg", back_populates="tinu")


class AssociationType(Base):
    __tablename__ = "associationtype"

    associationtype_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    association_type = Column(String)
    accepted_forms = Column(String)
    open_date = Column(TIMESTAMP)

    asso = relationship("Association", back_populates="assotype")
    commodities_type = relationship("AssociationTypeCommodities", back_populates="type_commodities")
    watertank = relationship("CommodityAccount", back_populates="assohouse")


class AssociationTypeCommodities(Base):
    __tablename__ = "association_type_commodities"

    association_type_commodity_id = Column(Integer, primary_key=True, index=True)
    association_type_id = Column(Integer, ForeignKey("associationtype.associationtype_id"))
    commodities_id = Column(Integer, ForeignKey("commodities.id"))

    type_commodities = relationship("AssociationType", back_populates="commodities_type")
    commodity_type = relationship("Commodities", back_populates="type_commodity")


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


class CommoditiesTransactionType(Base):
    __tablename__ = "commodity_transaction_type"

    id = Column(Integer, primary_key=True, index=True)
    commodity_transact_type = Column(String)

    nu_type = relationship("CommodityTransactions", back_populates="type_nu")


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
    repayment_starts = Column(DATE)
    repayment_ends = Column(DATE)

    loan_account = relationship("MemberLoanAccount", back_populates="loans_transactions")
    transaction_type = relationship("TransactionType", back_populates="loantransact")
    prepared_by = relationship("Users", back_populates="loans_transactions")
    loanadvise = relationship("LoanAdvise", back_populates="advise")


class LoanAdvise(Base):
    __tablename__ = "loan_advise"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String)
    interest_rate_percentage = Column(Integer)
    interest_rate_amount = Column(FLOAT)
    repayment_starting_date = Column(String)
    repayment_ending_date = Column(String)
    application_fee = Column(FLOAT)
    proccessing_fee = Column(FLOAT)
    loan_transaction_id = Column(Integer, ForeignKey("loans_transactions.transaction_id"))
    issue_date = Column(TIMESTAMP)

    advise = relationship("LoansTransaction", back_populates="loanadvise")


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
    slip = relationship("ShareCert", back_populates="transact")


class ShareCert(Base):
    __tablename__ = "share_cert"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String)
    interest_rate_percentage = Column(FLOAT)
    interest_rate_amount = Column(FLOAT)
    starting_date = Column(String)
    ending_date = Column(String)
    on_due_date = Column(String)
    spending_means = Column(String)
    share_transaction_id = Column(Integer, ForeignKey("shares_transactions.transaction_id"))

    transact = relationship("SharesTransaction", back_populates="slip")


class CommodityTransactions(Base):
    __tablename__ = "commodity_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    commodity_transaction_type_id = Column(Integer, ForeignKey("commodity_transaction_type.id"))
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(TIMESTAMP)
    commodity_acc_id = Column(Integer, ForeignKey("member_commodity_acc.id"))
    amount_of_commodity = Column(Integer)
    commodities_id = Column(Integer, ForeignKey("commodities.id"))

    thethings = relationship("Commodities", back_populates="thingsthe")
    type_nu = relationship("CommoditiesTransactionType", back_populates="nu_type")
    nipa_nu = relationship("Users", back_populates="nu_nipa")
    account_nso = relationship("MemberCommodityAccount", back_populates="nso_account")
