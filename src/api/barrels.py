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
                update_ml_query = sqlalchemy.text("UPDATE resources SET red_ml = red_ml + :ml_in_barrels")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))
        elif pot_type == [0,1,0,0]: #GREEN
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("UPDATE resources SET green_ml = green_ml + :ml_in_barrels")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))
        elif pot_type == [0,0,1,0]: #BLUE
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("UPDATE resources SET blue_ml = blue_ml + :ml_in_barrels")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))



    with db.engine.begin() as connection:
        update_gold_query = sqlalchemy.text("UPDATE resources SET gold = gold - :total_price")
        connection.execute(update_gold_query, parameters=(dict(total_price=total_price)))

    
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("Catalog: ",wholesale_catalog)

    with db.engine.begin() as connection:
        resources = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, gold FROM resources"))
        row = resources.first()

        red = row[0]
        green = row[1]
        blue = row[2]
        gold = row[3]

        min_ml = min(red, green, blue)

    if  gold >= 320:
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
    elif gold < 320:
         
         if gold < 120:
            if red == min_ml:
                return [
                    {
                        "sku": "SMALL_RED_BARREL",
                        "quantity": 1
                    }
                    ]
            elif green == min_ml:
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
    
