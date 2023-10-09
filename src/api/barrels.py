from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    total_price = 0
    ml_in_barrels = 0

    for barrel in barrels_delivered:
        total_price += barrel.price * barrel.quantity
        ml_in_barrels = barrel.ml_per_barrel * barrel.quantity

        with db.engine.begin() as connection:
            update_ml_query = sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :ml_in_barrels")
            connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))

    with db.engine.begin() as connection:
        update_gold_query = sqlalchemy.text("UPDATE global_inventory SET gold = gold - :total_price")
        connection.execute(update_gold_query, parameters=(dict(total_price=total_price)))

    
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("Catalog: ",wholesale_catalog)
    print("VERSION: ", sqlalchemy.__version__)

    with db.engine.begin() as connection:
        potions_result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory"))
        row = potions_result.first()

        red_potions = row[0]
        gold = row[1]



    if red_potions < 10 and gold >= 100:
         return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
         ]
    else:
        return {}
    
