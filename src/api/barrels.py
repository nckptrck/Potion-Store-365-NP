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
                update_ml_query = sqlalchemy.text("INSERT INTO potion_ingredients (red_change) VALUES (:ml_in_barrels)")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))
        elif pot_type == [0,1,0,0]: #GREEN
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("INSERT INTO potion_ingredients (green_change) VALUES (:ml_in_barrels)")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))
        elif pot_type == [0,0,1,0]: #BLUE
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("INSERT INTO potion_ingredients (blue_change) VALUES (:ml_in_barrels)")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))
        elif pot_type == [0,0,0,1]: #DARK
            with db.engine.begin() as connection:
                update_ml_query = sqlalchemy.text("INSERT INTO potion_ingredients (dark_change) VALUES (:ml_in_barrels)")
                connection.execute(update_ml_query, parameters=(dict(ml_in_barrels=ml_in_barrels)))



    with db.engine.begin() as connection:
        update_gold_query = sqlalchemy.text("INSERT INTO gold_ledger (change) VALUES (-:total_price)")
        connection.execute(update_gold_query, parameters=(dict(total_price=total_price)))

    
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("Catalog: ",wholesale_catalog)

    with db.engine.begin() as connection:
        resources = connection.execute(sqlalchemy.text("SELECT SUM(change) as gold FROM gold_ledger"))
        row = resources.first()
        gold = row[0]
        resources = connection.execute(sqlalchemy.text("SELECT SUM(red_change), SUM(green_change), SUM(blue_change), SUM(dark_change) FROM potion_ingredients")).first()
        total_ml = resources[0] + resources[1] + resources[2] + resources[3]
    
    #if total_ml >= 20000:
    #    return []

    
    
    med_red = False
    large_red = False
    med_green = False
    large_green = False
    med_blue = False
    barrels_copped = []
    for barrel in wholesale_catalog:
        sku = barrel.sku 
        #if sku == "LARGE_DARK_BARREL" and barrel.price <= gold:
        #   barrels_copped.append({"sku": sku,
        #                           "quantity": 1})
         #   gold -= barrel.price
        if sku == "MEDIUM_RED_BARREL":
            med_red = True
            mr_price = barrel.price
        elif sku == "MEDIUM_GREEN_BARREL":
            med_green = True
            mg_price = barrel.price
        elif sku == "LARGE_RED_BARREL":
            large_red = True
            lr_price = barrel.price
        elif sku == "LARGE_GREEN_BARREL":
            large_green = True
            lg_price = barrel.price
        elif sku == "MEDIUM_BLUE_BARREL" :
            med_blue = True
            mb_price = barrel.price
        else:
            continue
    
    if med_blue and large_green and large_red and gold >= (mb_price + lr_price + lg_price):
        barrels_copped.append({"sku": "MEDIUM_BLUE_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "LARGE_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "LARGE_GREEN_BARREL",
                               "quantity": 1})
        gold -= (mb_price + lr_price + lg_price)
    elif large_green and large_red and gold >= (lr_price + lg_price + 120):
        barrels_copped.append({"sku": "SMALL_BLUE_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "LARGE_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "LARGE_GREEN_BARREL",
                               "quantity": 1})
        gold -= (lr_price + lg_price + 120)
    elif large_green and large_red and gold >= (lr_price + lg_price):
        barrels_copped.append({"sku": "LARGE_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "LARGE_GREEN_BARREL",
                               "quantity": 1})
        gold -= (lr_price + lg_price)
    elif med_red and med_green and med_blue and gold >= (mr_price + mg_price + mb_price):
        barrels_copped.append({"sku": "MEDIUM_BLUE_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "MEDIUM_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "MEDIUM_GREEN_BARREL",
                               "quantity": 1})
        gold -= (mr_price + mg_price + mb_price)
    elif med_red and med_green and gold >= (mr_price + mg_price + 120):
        barrels_copped.append({"sku": "SMALL_BLUE_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "MEDIUM_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "MEDIUM_GREEN_BARREL",
                               "quantity": 1})
        gold -= (mr_price + mg_price + 120)
    elif med_red and med_green and gold >= (mr_price + mg_price):
        barrels_copped.append({"sku": "MEDIUM_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "MEDIUM_GREEN_BARREL",
                               "quantity": 1})
        gold -= (mr_price + mg_price)
    elif gold >= 320:
        barrels_copped.append({"sku": "SMALL_BLUE_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "SMALL_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "SMALL_GREEN_BARREL",
                               "quantity": 1})
        gold -= 320
    elif gold >= 200:
        barrels_copped.append({"sku": "SMALL_RED_BARREL",
                               "quantity": 1})
        barrels_copped.append({"sku": "SMALL_GREEN_BARREL",
                               "quantity": 1})
        gold -= 200
    elif gold >= 100:
        barrels_copped.append({"sku": "SMALL_RED_BARREL",
                               "quantity": 1})
        gold -= 100



    return barrels_copped
    
