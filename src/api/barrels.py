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
        pot_type = barrel.potion_type
        
        if pot_type == [1,0,0,0]: #RED
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :ml_in_barrels")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))
        elif pot_type == [0,1,0,0]: #GREEN
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :ml_in_barrels")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))
        elif pot_type == [0,0,1,0]: #BLUE
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + :ml_in_barrels")
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

    with db.engine.begin() as connection:
        potions_result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory"))
        row = potions_result.first()

        red_potions = row[0]
        green_potions = row[1]
        blue_potions = row[2]
        gold = row[3]

        min_potions = min(red_potions, green_potions, blue_potions)

    if  gold >= 300:
         return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }, 
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1,
        }, 
        {
            "sku": "SMALL_BLUE_BARREL",
            "quantity": 1,
        }
         ]
    elif gold < 300:
         if red_potions == min_potions:
            return [
                {
                    "sku": "SMALL_RED_BARREL",
                    "quantity": 1
                }
                ]
         elif green_potions == min_potions:
             return [
                {
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1
                }
                ]
         else: 
            return[
                {
                    "sku": "SMALL_BLUE_BARREL",
                    "quantity": 1
                }
                ]


    else:
        return {}
    
