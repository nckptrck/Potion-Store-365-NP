from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    num_potions = potions_delivered[0].quantity
    num_ml = num_potions * 100
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + :num_potions"), parameters= dict(num_potions = num_potions))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :num_ml"), parameters= dict(num_ml = num_ml))
    print(potions_delivered)

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        potions_result = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
    
    row = potions_result.first()
    red_ml = row[0]
    if red_ml >= 100:
        make_potions = red_ml // 100
        return [
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": make_potions,
                }
            ]
    else:
         return {}
