import sys

from sqlalchemy import desc, func

sys.path.append("../..")

from typing import Optional, List
from fastapi import Depends, HTTPException, APIRouter, status
import models
from collections import defaultdict
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, get_user_exception
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from routers.accounts import process_storage

router = APIRouter(
    prefix="/commodity",
    tags=["commodities"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/type/commodities/{society_id}")
async def get_society_commodities(society_id: int,
                                  user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    # commodities = db.query(models.Commodities.commodity) \
    #     .select_from(models.AssociationType) \
    #     .join(models.AssociationTypeCommodities,
    #           models.AssociationTypeCommodities.association_type_id == models.AssociationType.associationtype_id) \
    #     .join(models.Commodities, models.Commodities.id == models.AssociationTypeCommodities.commodities_id) \
    #     .filter(models.AssociationType.associationtype_id == associationtype_id) \
    #     .all()
    #
    # units = db.query(models.UnitsKg.unit_per_kg) \
    #     .select_from(models.AssociationType) \
    #     .join(models.AssociationTypeCommodities,
    #           models.AssociationTypeCommodities.association_type_id == models.AssociationType.associationtype_id) \
    #     .join(models.Commodities, models.Commodities.id == models.AssociationTypeCommodities.commodities_id) \
    #     .join(models.CommodityUnitsJoin, models.Commodities.id == models.CommodityUnitsJoin.commodity_id) \
    #     .join(models.UnitsKg, models.UnitsKg.id == models.CommodityUnitsJoin.unit_per_kg_id) \
    #     .filter(models.AssociationType.associationtype_id == associationtype_id) \
    #     .all()
    # prices = db.query(models.CommodityGradeValues.grade,
    #                   models.CommodityGradeValues.price_per_kg) \
    #     .select_from(models.AssociationType) \
    #     .join(models.AssociationTypeCommodities,
    #           models.AssociationTypeCommodities.association_type_id == models.AssociationType.associationtype_id) \
    #     .join(models.Commodities, models.Commodities.id == models.AssociationTypeCommodities.commodities_id) \
    #     .join(models.CommodityUnitsJoin, models.Commodities.id == models.CommodityUnitsJoin.commodity_id) \
    #     .join(models.CommodityGradeValues, models.CommodityGradeValues.commodities_id == models.Commodities.id) \
    #     .filter(models.AssociationType.associationtype_id == associationtype_id) \
    #     .all()

    # all_dem = db.query(models.Commodities.id,
    #                    models.Commodities.commodity,
    #                    func.array_agg(models.UnitsKg.unit_per_kg).label('unit_per_kg_list'),
    #                    models.CommodityGradeValues.grade,
    #                    models.CommodityGradeValues.price_per_kg
    #                    ) \
    #     .select_from(models.AssociationType) \
    #     .join(models.AssociationTypeCommodities,
    #           models.AssociationTypeCommodities.association_type_id == models.AssociationType.associationtype_id) \
    #     .join(models.Commodities, models.Commodities.id == models.AssociationTypeCommodities.commodities_id) \
    #     .join(models.CommodityUnitsJoin, models.Commodities.id == models.CommodityUnitsJoin.commodity_id) \
    #     .join(models.UnitsKg, models.UnitsKg.id == models.CommodityUnitsJoin.unit_per_kg_id) \
    #     .join(models.CommodityGradeValues, models.CommodityGradeValues.commodities_id == models.Commodities.id) \
    #     .filter(models.AssociationType.associationtype_id == associationtype_id) \
    #     .order_by(desc(models.Commodities.id)) \
    #     .all()
    # .group_by(
    #     models.Commodities.id,
    #     models.Commodities.commodity,
    #     models.CommodityGradeValues.grade,
    #     models.CommodityGradeValues.price_per_kg
    # ) \
    #         unique_tracks = defaultdict(list)
    #
    # for row in all_dem:
    #     row_identifier = (
    #         # row.id,
    #         row.commodity,
    #         # row.unit_per_kg_list,
    #         # row.grade,
    #         row.price_per_kg
    #     )
    #
    #     if row_identifier not in unique_tracks:
    #         unique_tracks[row_identifier] = row
    #
    # filtered_tracks = list(unique_tracks.values())
    # print(all_dem)
    # return {"Commodities": all_dem}
    # Commodities = aliased(Commodities)
    # UnitsKg = aliased(UnitsKg)
    # CommodityGradeValues = aliased(CommodityGradeValues)

    # Build the query

    query = (
        db.query(
            models.Commodities.commodity,
            models.Commodities.id,
            func.array_agg(models.UnitsKg.unit_per_kg).label('unit_per_kg_list'),
            func.array_agg(models.CommodityGradeValues.grade).label('grade_list'),
            func.array_agg(models.CommodityGradeValues.price_per_kg).label('price_per_kg_list')
        )
        .select_from(models.Commodities)
        .join(models.CommodityUnitsJoin, models.Commodities.id == models.CommodityUnitsJoin.commodity_id)
        .join(models.UnitsKg, models.UnitsKg.id == models.CommodityUnitsJoin.unit_per_kg_id)
        .join(models.CommodityGradeValues, models.CommodityGradeValues.commodities_id == models.Commodities.id)
        .join(models.SocietyCommodities,
              models.SocietyCommodities.commodities_id == models.Commodities.id)
        .join(models.Society,
              models.Society.id == models.SocietyCommodities.society_id)
        .filter(models.Society.id == society_id)
        .group_by(models.Commodities.commodity,
                  models.Commodities.id, )
    )

    result = query.all()

    unique_unit_per_kg = defaultdict(set)
    unique_grade = defaultdict(set)
    unique_price_per_kg = defaultdict(set)

    for row in result:
        unique_unit_per_kg[row.id].update(row.unit_per_kg_list)
        unique_grade[row.id].update(row.grade_list)
        unique_price_per_kg[row.id].update(row.price_per_kg_list)

    commodity_data = [
        {
            "Id": row.id,
            "commodity": row.commodity,
            "unit_per_kg_list": " | ".join(map(str, unique_unit_per_kg[row.id])),
            "grade_list": " | ".join(sorted(map(str, unique_grade[row.id]))),
            "price_per_kg_list": " | ".join(sorted(map(str, unique_price_per_kg[row.id]))[::-1]),
        }
        for row in result
    ]
    # print(commodity_data)
    return {"Commodities": commodity_data}


class CommoditiesCreate(BaseModel):
    commodity: str
    society_id: int
    unit_per_kg: List[int]
    grade: List[str]
    price_per_kg: List[float]


@router.post("/create/commodity")
async def create_new_commodity(data_nkoa: CommoditiesCreate,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    commodity_model = models.Commodities()
    commodity_model.commodity = data_nkoa.commodity

    db.add(commodity_model)
    db.flush()
    db.commit()

    commodity_id = db.query(models.Commodities) \
        .order_by(desc(models.Commodities.id)) \
        .first()

    for unit in data_nkoa.unit_per_kg:
        adder = models.UnitsKg(
            unit_per_kg=unit
        )
        db.add(adder)
        db.commit()

        unit_per_kg_id = adder.id

        commodity_units_join = models.CommodityUnitsJoin(
            commodity_id=commodity_id.id,
            unit_per_kg_id=unit_per_kg_id
        )
        db.add(commodity_units_join)
        db.commit()

    for i in range(len(data_nkoa.grade)):
        grade = data_nkoa.grade[i]
        price = data_nkoa.price_per_kg[i]

        grade_value = models.CommodityGradeValues(
            commodities_id=commodity_id.id,
            price_per_kg=price,
            grade=grade
        )
        db.add(grade_value)
        db.flush()
        db.commit()
        units = db.query(models.UnitsKg.id) \
            .select_from(models.CommodityUnitsJoin) \
            .join(models.UnitsKg, models.UnitsKg.id == models.CommodityUnitsJoin.unit_per_kg_id) \
            .order_by(desc(models.UnitsKg.id)) \
            .first()
        store_track = models.CommodityValueTrack(
            commodities_id=commodity_id.id,
            date=datetime.now(),
            new_price_per_kg=price,
            grade=grade,
            new_units_per_kg=units.id
        )
        db.add(store_track)
        db.commit()

    addings = models.SocietyCommodities(
        society_id=data_nkoa.society_id,
        commodities_id=commodity_id.id
    )
    db.add(addings)
    db.commit()

    return "New Commodity Added"


class SetNewPrice(BaseModel):
    Id: int
    grade: List[str]
    price_per_kg: List[float]


@router.put("/price/change")
async def set_price_change(new: SetNewPrice,
                           user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    old = db.query(models.CommodityGradeValues) \
        .filter(models.CommodityGradeValues.commodities_id == new.Id) \
        .all()
    if not old:
        raise HTTPException(status_code=404, detail="Price not found")

    changes = []

    for i in range(len(old)):
        if new.grade[i] != old[i].grade:
            new.grade[i] = old[i].grade

        grade = new.grade[i]
        price = new.price_per_kg[i]

        if old[i].grade != grade or old[i].price_per_kg != price:
            changes.append({
                "grade": grade,
                "price_per_kg": price
            })

        old[i].grade = grade
        old[i].price_per_kg = price

        # db.add(old)
        db.commit()

        new_price = db.query(models.CommodityGradeValues) \
            .filter(models.CommodityGradeValues.commodities_id == new.Id) \
            .all()
        for change in changes:
            units = db.query(models.UnitsKg.id) \
                .select_from(models.CommodityUnitsJoin) \
                .join(models.UnitsKg, models.UnitsKg.id == models.CommodityUnitsJoin.unit_per_kg_id) \
                .filter(models.CommodityUnitsJoin.commodity_id == new.Id) \
                .first()

            store_track = models.CommodityValueTrack(
                commodities_id=new.Id,
                date=datetime.now(),
                new_price_per_kg=change["price_per_kg"],
                grade=change["grade"],
                new_units_per_kg=units.id
            )
            db.add(store_track)
            db.commit()
    trs = db.query(models.CommodityTransactions) \
        .filter(models.CommodityTransactions.commodities_id == new.Id) \
        .all()

    for item in trs:
        new_man = await process_storage(
            commodity_id=new.Id,
            grade_id=item.grade_id,
            unit_id=item.units_id,
            amount_storing=item.amount_of_commodity,
            member_com_acc=item.commodity_acc_id,
            rebag=item.rebagging_fee,
            stack=item.stacking_fee,
            clean=item.cleaning_fee,
            destone=item.destoning_fee,
            store=item.storage_fee,
            stitch=item.stitching_fee,
            load=item.loading_fee,
            empty_sack=item.empty_sack_cost_fee,
            user=user,
            db=db,
        )
        balance = item.total_cash_balance - item.cash_value
        item.cash_value = new_man.get("total_cash_value")
        item.total_cash_balance = balance + new_man.get("total_cash_value")
        db.commit()

        foward_balance = db.query(models.CommodityTransactions) \
            .filter(models.CommodityTransactions.commodity_acc_id == item.commodity_acc_id,
                    func.date(models.CommodityTransactions.transaction_date) > func.date(item.transaction_date),
                    models.CommodityTransactions.transaction_id != item.transaction_id) \
            .all()
        forw_bal = item.total_cash_balance - (balance + new_man.get("total_cash_value"))

        for iet in foward_balance:
            iet.total_cash_balance += forw_bal
            db.commit()
        set_for_acc = db.query(models.CommodityTransactions) \
            .filter(models.CommodityTransactions.commodity_acc_id == item.commodity_acc_id) \
            .order_by(desc(models.CommodityTransactions.transaction_id)) \
            .first()
        mem_acc = db.query(models.MemberCommodityAccount) \
            .filter(models.MemberCommodityAccount.id == item.commodity_acc_id) \
            .first()
        mem_acc.cash_value = set_for_acc.total_cash_balance
        db.commit()

        member_commodity = db.query(models.MemberCommodityAccCommodities) \
            .filter(models.MemberCommodityAccCommodities.member_acc_id == item.commodity_acc_id,
                    models.MemberCommodityAccCommodities.commodities_id == item.commodities_id) \
            .first()
        cash_vl = member_commodity.commodity_cash_value - item.cash_value
        member_commodity.commodity_cash_value = cash_vl + new_man.get("total_cash_value")
        db.commit()

    return "Price updated successfully"


@router.get("/prices/track")
async def get_price_traking_table(user: dict = Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    result = db.query(models.Commodities.commodity,
                      models.CommodityValueTrack.id,
                      models.CommodityValueTrack.date,
                      models.CommodityValueTrack.new_price_per_kg,
                      models.CommodityValueTrack.grade) \
        .select_from(models.CommodityValueTrack) \
        .join(models.Commodities, models.Commodities.id == models.CommodityValueTrack.commodities_id) \
        .join(models.SocietyCommodities, models.Commodities.id == models.SocietyCommodities.commodities_id) \
        .filter(models.Commodities.id == models.SocietyCommodities.commodities_id) \
        .order_by(desc(models.CommodityValueTrack.id)) \
        .all()

    unique_tracks = defaultdict(list)

    for row in result:
        row_identifier = (
            row.commodity,
            row.date,
            row.grade,
            row.new_price_per_kg
        )

        if row_identifier not in unique_tracks:
            unique_tracks[row_identifier] = row

    filtered_tracks = list(unique_tracks.values())

    return {"Tracks": filtered_tracks}
