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


@router.get("/type/commodities/{associationtype_id}")
async def get_association_type_commodities(associationtype_id: int,
                                           user: dict = Depends(get_current_user),
                                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    commodities = db.query(models.Commodities.commodity) \
        .select_from(models.AssociationType) \
        .join(models.AssociationTypeCommodities,
              models.AssociationTypeCommodities.association_type_id == models.AssociationType.associationtype_id) \
        .join(models.Commodities, models.Commodities.id == models.AssociationTypeCommodities.commodities_id) \
        .filter(models.AssociationType.associationtype_id == associationtype_id) \
        .all()

    units = db.query(models.UnitsKg.unit_per_kg) \
        .select_from(models.AssociationType) \
        .join(models.AssociationTypeCommodities,
              models.AssociationTypeCommodities.association_type_id == models.AssociationType.associationtype_id) \
        .join(models.Commodities, models.Commodities.id == models.AssociationTypeCommodities.commodities_id) \
        .join(models.CommodityUnitsJoin, models.Commodities.id == models.CommodityUnitsJoin.commodity_id) \
        .join(models.UnitsKg, models.UnitsKg.id == models.CommodityUnitsJoin.unit_per_kg_id) \
        .filter(models.AssociationType.associationtype_id == associationtype_id) \
        .all()
    prices = db.query(models.CommodityGradeValues.grade,
                      models.CommodityGradeValues.price_per_kg) \
        .select_from(models.AssociationType) \
        .join(models.AssociationTypeCommodities,
              models.AssociationTypeCommodities.association_type_id == models.AssociationType.associationtype_id) \
        .join(models.Commodities, models.Commodities.id == models.AssociationTypeCommodities.commodities_id) \
        .join(models.CommodityUnitsJoin, models.Commodities.id == models.CommodityUnitsJoin.commodity_id) \
        .join(models.CommodityGradeValues, models.CommodityGradeValues.commodities_id == models.Commodities.id) \
        .filter(models.AssociationType.associationtype_id == associationtype_id) \
        .all()



# all_dem = db.query(models.Commodities.commodity,
    #                    models.UnitsKg.unit_per_kg,
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
    #     .all()


    # return {"Commodities": all_dem}
    # seen_dem = set()
    # all_of_data = []
    #
    # for como_data in all_dem:
    #     (
    #         commodity,
    #         unit_per_kg,
    #         grade,
    #         price_per_kg
    #     ) = como_data
    #
    #     if commodity not in seen_dem:
    #         seen_dem.add(commodity)
    #         all_of_data.append({
    #             "commodity": commodity,
    #             "unit_per_kg": unit_per_kg,
    #             "grade": grade,
    #             "price_per_kg": price_per_kg
    #         })

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
        .join(models.AssociationTypeCommodities, models.AssociationTypeCommodities.commodities_id == models.Commodities.id)
        .join(models.AssociationType, models.AssociationType.associationtype_id == models.AssociationTypeCommodities.association_type_id)
        .filter(models.AssociationType.associationtype_id == associationtype_id)
        .group_by(models.Commodities.commodity,
                  models.Commodities.id,)
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

    return {"Commodities": commodity_data}




class CommoditiesCreate(BaseModel):
    commodity: str
    associationtype_id: int
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
            grade=grade,
            price_per_kg=price,
            commodities_id=commodity_id.id
        )
        db.add(grade_value)
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

    addings = models.AssociationTypeCommodities(
        association_type_id=data_nkoa.associationtype_id,
        commodities_id=commodity_id.id
    )
    db.add(addings)
    db.commit()

    return "New Commodity Added"

# @router.put("/setprice")
# async def set_price_change()
