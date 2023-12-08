from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, UniqueConstraint, Boolean, DateTime, Date, \
    Float
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
    role_id = Column(Integer, ForeignKey("user_roles.id"))
    date_joined = Column(DateTime)
    society_id = Column(Integer, ForeignKey("society.id"))

    soc = relationship("Society", back_populates="usesoc")
    savings_transactions = relationship("SavingsTransaction", back_populates="prepared_by")
    loans_transactions = relationship("LoansTransaction", back_populates="prepared_by")
    shares_transactions = relationship("SharesTransaction", back_populates="prepared_by")
    momos_transactions = relationship("MomoAccountTransactions", back_populates="prepared_by")
    info = relationship("UserInfo", back_populates="user")
    user_staff = relationship("Association", foreign_keys="Association.staff_userid", back_populates="staff_user")
    user_creator = relationship("Association", foreign_keys="Association.created_by", back_populates="creator")
    nu_nipa = relationship("CommodityTransactions", back_populates="nipa_nu")
    doer = relationship("SocietyBankAccounts", back_populates="use")
    sotra = relationship("SocietyTransactions", back_populates="prepBy")
    reconchat = relationship("ReconciliationChats", back_populates="fro")
    rollers = relationship("UserRoles", back_populates="users_role")
    account = relationship("UserAccount", back_populates="user")


class UserInfo(Base):
    __tablename__ = "user_info"

    userinfo_id = Column(Integer, primary_key=True, index=True)
    dob = Column(Date)
    gender = Column(String)
    address = Column(String)
    phone = Column(String)
    userImage = Column(LargeBinary)
    users_id = Column(Integer, ForeignKey("users.id"))
    marital_status = Column(String)
    sinn_number = Column(String)
    basic_salary = Column(Float, nullable=True)
    bank_name = Column(String)
    account_number = Column(Integer, nullable=True)
    account_name = Column(String)

    user = relationship("Users", back_populates="info")


class UserAccount(Base):
    __tablename__ = "user_account"

    user_account_id = Column(Integer, primary_key=True, index=True)
    current_balance = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="account")
    user_account_transactions = relationship("UserAccountTransactions", back_populates="user_account")


class UserAccountTransactions(Base):
    __tablename__ = "user_account_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_account_id = Column(Integer, ForeignKey("user_account.user_account_id"))
    amount = Column(Float)
    transaction_type_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    request_date = Column(DateTime)
    disburse_date = Column(DateTime)
    narration = Column(String)
    balance = Column(Float)
    status = Column(String)
    message_id = Column(Integer, ForeignKey("approval_message.id"))

    user_account = relationship("UserAccount", back_populates="user_account_transactions")
    transaction_type = relationship("TransactionType", back_populates="user_account_transactions")
    approval_message = relationship("ApprovalMessage", back_populates="user_account_transactions")


class ApprovalMessage(Base):
    __tablename__ = "approval_message"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)

    user_account_transactions = relationship("UserAccountTransactions", back_populates="approval_message")


class UserRoles(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String)
    create_member = Column(Boolean, nullable=True)
    update_member = Column(Boolean)
    delete_member = Column(Boolean)
    view_member = Column(Boolean)
    create_association = Column(Boolean)
    update_association = Column(Boolean)
    view_association = Column(Boolean)
    delete_association = Column(Boolean)
    create_society = Column(Boolean)
    update_society = Column(Boolean)
    view_society = Column(Boolean)
    delete_society = Column(Boolean)
    create_association_type = Column(Boolean)
    update_association_type = Column(Boolean)
    view_association_type = Column(Boolean)
    delete_association_type = Column(Boolean)
    create_savings_transactions = Column(Boolean)
    update_savings_transactions = Column(Boolean)
    view_savings_transactions = Column(Boolean)
    delete_savings_transactions = Column(Boolean)
    request_loan_transactions = Column(Boolean)
    update_loan_request = Column(Boolean)
    view_loan_transactions = Column(Boolean)
    delete_loan_transactions = Column(Boolean)
    download_loan_advise = Column(Boolean)
    approve_loan_requests = Column(Boolean)
    disburse_approved_loans = Column(Boolean)
    create_shares_transactions = Column(Boolean)
    view_share_transactions = Column(Boolean)
    download_share_cert = Column(Boolean)
    delete_share_transactions = Column(Boolean)
    view_association_passbook = Column(Boolean)
    view_association_momo_account = Column(Boolean)
    set_association_momo_bal = Column(Boolean)
    view_society_account = Column(Boolean)
    view_society_reconciliatio_form = Column(Boolean)
    reconcile_balances = Column(Boolean)
    view_bank_accounts = Column(Boolean)
    create_bank_accounts = Column(Boolean)
    create_bank_transactions = Column(Boolean)
    view_bank_transactions = Column(Boolean)
    update_bank_transactions = Column(Boolean)
    delete_bank_transactions = Column(Boolean)
    create_savings_account = Column(Boolean)
    update_savings_account = Column(Boolean)
    delete_savings_account = Column(Boolean)
    create_loan_account = Column(Boolean)
    update_loan_account = Column(Boolean)
    delete_loan_account = Column(Boolean)
    create_share_account = Column(Boolean)
    update_share_account = Column(Boolean)
    delete_share_account = Column(Boolean)
    create_warehouse = Column(Boolean)
    create_commodity = Column(Boolean)
    view_savings_account = Column(Boolean)
    view_loans_account = Column(Boolean)
    view_shares_account = Column(Boolean)
    view_commodity_account = Column(Boolean)
    view_warehouse = Column(Boolean)
    view_expense = Column(Boolean)
    expense_approve = Column(Boolean)
    expense_disbures = Column(Boolean)
    view_rejected = Column(Boolean)

    users_role = relationship("Users", back_populates="rollers")


class Members(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    middlename = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(String)
    phone = Column(String, nullable=True)
    otherPhone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    otherAddress = Column(String, nullable=True)
    ghcardnumber = Column(String, nullable=True)
    ghCardImage = Column(LargeBinary, nullable=True)
    memberImage = Column(LargeBinary, nullable=True)
    nextOfKin = Column(String, nullable=True)
    otherName = Column(String, nullable=True)
    commonname = Column(String, nullable=True)
    MaritalStatus = Column(String, nullable=True)
    EducationLevel = Column(String, nullable=True)
    Town = Column(String, nullable=True)
    ruralOrUrban = Column(String, nullable=True)


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
    is_refundable = Column(Boolean)
    medium_of_exchange = Column(String)
    interest_over_a_year = Column(Float)
    stamp_value = Column(Float)

    okihr = relationship("MemberSavingsAccount", back_populates="save")


class LoanAccount(Base):
    __tablename__ = "loan_account"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    interest_amt = Column(Float)
    application_fee = Column(Float)
    proccessing_fee = Column(Float)
    min_amt = Column(Float)
    max_amt = Column(Float)

    member_loan = relationship("MemberLoanAccount", back_populates="loan")


class ShareAccount(Base):
    __tablename__ = "share_account"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    share_value = Column(Float)
    interest_amt = Column(Float)

    shareme = relationship("MemberShareAccount", back_populates="share")


class Commodities(Base):
    __tablename__ = 'commodities'

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String)

    tracked = relationship("CommodityValueTrack", back_populates="tracker")
    thingsthe = relationship("CommodityTransactions", back_populates="thethings")
    ankasa_com = relationship("MemberCommodityAccCommodities", back_populates="com_ankasa")
    type_commodity = relationship("SocietyCommodities", back_populates="commodity_type")
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
    price_per_kg = Column("price/kg", Float)
    commodities_id = Column(Integer, ForeignKey("commodities.id"))

    grader = relationship("Commodities", back_populates="redarg")


class CommodityAccount(Base):
    __tablename__ = "commodity_account"

    id = Column(Integer, primary_key=True, index=True)
    warehouse = Column(String)
    community = Column(String)
    society_id = Column(Integer, ForeignKey("society.id"))
    rebagging_fee = Column(Float)
    stacking_fee = Column(Float)
    destoning_fee = Column(Float)
    cleaning_fee = Column(Float)
    storage_fee = Column(Float)
    tax_fee = Column(Float)
    stitching_fee = Column(Float)
    loading_fee = Column(Float)
    empty_sack_cost_fee = Column(Float)

    assohouse = relationship("Society", back_populates="watertank")
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
    date = Column(DateTime)
    new_price_per_kg = Column(Float)
    grade = Column(String)
    new_units_per_kg = Column("new_units/kg", Integer)

    tracker = relationship("Commodities", back_populates="tracked")


class MemberSavingsAccount(Base):
    __tablename__ = "member_savings_acc"

    id = Column(Integer, primary_key=True, index=True)
    savings_id = Column(Integer, ForeignKey("savings_accounts.id"))
    open_date = Column(DateTime)
    current_balance = Column(Float)
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
    open_date = Column(DateTime)
    current_balance = Column(Float)
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
    open_date = Column(DateTime)
    current_balance = Column(Float)
    association_member_id = Column(Integer, ForeignKey("associationmembers.association_members_id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))

    loans_transactions = relationship("LoansTransaction", back_populates="loan_account")
    loan = relationship("LoanAccount", back_populates="member_loan")
    membersowwn = relationship("Members", back_populates="member_members")
    passbookk = relationship("AssociationMembers", back_populates="passingg")


class MemberCommodityAccount(Base):
    __tablename__ = "member_commodity_acc"

    id = Column(Integer, primary_key=True, index=True)
    open_date = Column(DateTime)
    cash_value = Column(Float)
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
    commodity_cash_value = Column(Float)
    wieght = Column(Integer)
    tons = Column(Integer)

    acc_things = relationship("MemberCommodityAccount", back_populates="things_acc")
    com_ankasa = relationship("Commodities", back_populates="ankasa_com")
    unit = relationship("UnitsKg", back_populates="tinu")


class AssociationType(Base):
    __tablename__ = "associationtype"

    associationtype_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    association_type = Column(String)
    accepted_forms = Column(String, nullable=True)
    open_date = Column(DateTime)
    society_id = Column(Integer, ForeignKey("society.id"))

    asso = relationship("Association", back_populates="assotype")
    society = relationship("Society", back_populates="association")


class Society(Base):
    __tablename__ = "society"

    id = Column(Integer, primary_key=True, index=True)
    society = Column(String)

    usesoc = relationship("Users", back_populates="soc")
    association = relationship("AssociationType", back_populates="society")
    accbank = relationship("SocietyBankAccounts", back_populates="bankacc")
    watertank = relationship("CommodityAccount", back_populates="assohouse")
    commodities_type = relationship("SocietyCommodities", back_populates="type_commodities")


class SocietyBankAccounts(Base):
    __tablename__ = "society_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    open_date = Column(String)
    current_balance = Column(Float)
    society_id = Column(Integer, ForeignKey("society.id"))
    purpose = Column(String, nullable=True)
    opened_by = Column(Integer, ForeignKey("users.id"))

    use = relationship("Users", back_populates="doer")
    bankacc = relationship("Society", back_populates="accbank")
    acsotra = relationship("SocietyTransactions", back_populates="trasoac")


class SocietyCommodities(Base):
    __tablename__ = "society_commodities"

    society_commodity_id = Column(Integer, primary_key=True, index=True)
    society_id = Column(Integer, ForeignKey("society.id"))
    commodities_id = Column(Integer, ForeignKey("commodities.id"))

    type_commodities = relationship("Society", back_populates="commodities_type")
    commodity_type = relationship("Commodities", back_populates="type_commodity")


class Association(Base):
    __tablename__ = "association"

    association_id = Column(Integer, primary_key=True, index=True)
    association_name = Column(String, nullable=False)
    association_type_id = Column(Integer, ForeignKey("associationtype.associationtype_id"))
    community_name = Column(String)
    open_date = Column(Date)
    facilitator_userid = Column(Integer, ForeignKey("users.id"))
    association_email = Column(String, nullable=True)
    cluster_office = Column(String)
    staff_userid = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    staff_user = relationship("Users", foreign_keys="[Association.staff_userid]", back_populates="user_staff")
    creator = relationship("Users", foreign_keys="[Association.created_by]", back_populates="user_creator")
    members = relationship("AssociationMembers", back_populates="memasso")
    assotype = relationship("AssociationType", back_populates="asso")
    leader = relationship("AssociationLeaders", back_populates="associa")
    asoAc = relationship("MomoAccountAssociation", back_populates="momo")
    asoCashAc = relationship("CashAssociationAccount", back_populates="cash")
    momo_transactions = relationship("MomoAccountTransactions", back_populates="momo_account")


class CashAssociationAccount(Base):
    __tablename__ = "cash_association_account"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    cash_savings_bal = Column(Float)
    cash_loans_bal = Column(Float)
    cash_shares_bal = Column(Float)
    association_id = Column(Integer, ForeignKey("association.association_id"))
    cash_value = Column(Float)
    withdrawal_value = Column(Float)
    transfers_value = Column(Float)
    loan_disbursed = Column(Float)

    cash = relationship("Association", back_populates="asoCashAc")


class MomoAccountAssociation(Base):
    __tablename__ = "momo_account_association"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    momo_bal = Column(Float)
    association_id = Column(Integer, ForeignKey("association.association_id"))
    status = Column(String)
    button = Column(String)
    current_balance = Column(Float)

    momo = relationship("Association", back_populates="asoAc")
    ba = relationship("ReconciliationNote", back_populates="mo")
    conre = relationship("ReconciliationChats", back_populates="recon")


class MomoAccountTransactions(Base):
    __tablename__ = "momo_account_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(Float)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(DateTime)
    association_id = Column(Integer, ForeignKey("association.association_id"))
    balance = Column(Float, nullable=True)

    momo_account = relationship("Association", back_populates="momo_transactions")
    transaction_style = relationship("TransactionType", back_populates="momo_style_transactions")
    prepared_by = relationship("Users", back_populates="momos_transactions")

class ReconciliationNote(Base):
    __tablename__ = "reconciliation_note"

    id = Column(Integer, primary_key=True, index=True)
    note = Column(String, nullable=True)
    momo_id = Column(Integer, ForeignKey("momo_account_association.id"))

    mo = relationship("MomoAccountAssociation", back_populates="ba")


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
    passbook_id = Column(String, nullable=True)

    assomem = relationship("Members", back_populates="association")
    memasso = relationship("Association", back_populates="members")
    passing = relationship("MemberCommodityAccount", back_populates="passbook")
    passingg = relationship("MemberLoanAccount", back_populates="passbookk")
    money = relationship("MemberShareAccount", back_populates="memss")
    okiwill = relationship("MemberSavingsAccount", back_populates="passsave")


class TransactionType(Base):
    __tablename__ = "transaction_type"

    transactype_id = Column(Integer, primary_key=True, index=True)
    transactiontype_name = Column(String)

    savings_transactions = relationship("SavingsTransaction", back_populates="transaction_type")
    loantransact = relationship("LoansTransaction", back_populates="transaction_type")
    sharetransact = relationship("SharesTransaction", back_populates="transaction_type")
    tpytra = relationship("SocietyTransactions", back_populates="sotype")
    user_account_transactions = relationship("UserAccountTransactions", back_populates="transaction_type")
    momo_style_transactions = relationship("MomoAccountTransactions", back_populates="transaction_style")


class CommoditiesTransactionType(Base):
    __tablename__ = "commodity_transaction_type"

    id = Column(Integer, primary_key=True, index=True)
    commodity_transact_type = Column(String)

    nu_type = relationship("CommodityTransactions", back_populates="type_nu")


class ReconciliationChats(Base):
    __tablename__ = "reconciliation_chats"

    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, ForeignKey("users.id"))
    to_recon_id = Column(Integer, ForeignKey("momo_account_association.id"))
    message = Column(String, nullable=True)

    fro = relationship("Users", back_populates="reconchat")
    recon = relationship("MomoAccountAssociation", back_populates="conre")


class SocietyTransactions(Base):
    __tablename__ = "society_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transactiontype_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(Float)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String, nullable=True)
    transaction_date = Column(DateTime)
    balance = Column(Float)
    society_account_id = Column(Integer, ForeignKey("society_bank_accounts.id"))

    prepBy = relationship("Users", back_populates="sotra")
    sotype = relationship("TransactionType", back_populates="tpytra")
    trasoac = relationship("SocietyBankAccounts", back_populates="acsotra")


class SavingsTransaction(Base):
    __tablename__ = "savings_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transactiontype_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(Float)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(DateTime)
    savings_acc_id = Column(Integer, ForeignKey("member_savings_acc.id"))
    balance = Column(Float, nullable=True)

    savings_account = relationship("MemberSavingsAccount", back_populates="savings_transactions")
    transaction_type = relationship("TransactionType", back_populates="savings_transactions")
    prepared_by = relationship("Users", back_populates="savings_transactions")


class LoansTransaction(Base):
    __tablename__ = "loans_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transactiontype_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(Float)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(DateTime)
    loans_acc_id = Column(Integer, ForeignKey("member_loan_acc.id"))
    status = Column(String)
    repayment_starts = Column(Date)
    repayment_ends = Column(Date)
    balance = Column(Float, nullable=True)
    message = Column(String, nullable=True)
    time = Column(String)

    loan_account = relationship("MemberLoanAccount", back_populates="loans_transactions")
    transaction_type = relationship("TransactionType", back_populates="loantransact")
    prepared_by = relationship("Users", back_populates="loans_transactions")
    loanadvise = relationship("LoanAdvise", back_populates="advise")


class LoanAdvise(Base):
    __tablename__ = "loan_advise"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String)
    interest_rate_percentage = Column(Float)
    interest_rate_amount = Column(Float)
    repayment_starting_date = Column(String)
    repayment_ending_date = Column(String)
    application_fee = Column(Float)
    proccessing_fee = Column(Float)
    loan_transaction_id = Column(Integer, ForeignKey("loans_transactions.transaction_id"))
    issue_date = Column(DateTime)

    advise = relationship("LoansTransaction", back_populates="loanadvise")


class SharesTransaction(Base):
    __tablename__ = "shares_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    transactiontype_id = Column(Integer, ForeignKey("transaction_type.transactype_id"))
    amount = Column(Float)
    prep_by = Column(Integer, ForeignKey("users.id"))
    narration = Column(String)
    transaction_date = Column(DateTime)
    shares_acc_id = Column(Integer, ForeignKey("member_share_acc.id"))
    balance = Column(Float, nullable=True)

    shares_accounts = relationship("MemberShareAccount", back_populates="shares_transactions")
    transaction_type = relationship("TransactionType", back_populates="sharetransact")
    prepared_by = relationship("Users", back_populates="shares_transactions")
    slip = relationship("ShareCert", back_populates="transact")


class ShareCert(Base):
    __tablename__ = "share_cert"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String)
    interest_rate_percentage = Column(Float)
    interest_rate_amount = Column(Float)
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
    transaction_date = Column(DateTime)
    commodity_acc_id = Column(Integer, ForeignKey("member_commodity_acc.id"))
    amount_of_commodity = Column(Integer)
    commodities_id = Column(Integer, ForeignKey("commodities.id"))
    balance = Column(Float, nullable=True)

    thethings = relationship("Commodities", back_populates="thingsthe")
    type_nu = relationship("CommoditiesTransactionType", back_populates="nu_type")
    nipa_nu = relationship("Users", back_populates="nu_nipa")
    account_nso = relationship("MemberCommodityAccount", back_populates="nso_account")
