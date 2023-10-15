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

    for potion in potions_delivered:
        num_potions = potion.quantity
        num_ml = num_potions * 100

        if potion.potion_type == [100,0,0,0]: #RED
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + :num_potions"), parameters= dict(num_potions = num_potions))
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :num_ml"), parameters= dict(num_ml = num_ml))
        elif potion.potion_type == [0,100,0,0]: #GREEN
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :num_potions"), parameters= dict(num_potions = num_potions))
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - :num_ml"), parameters= dict(num_ml = num_ml))
        elif potion.potion_type == [0,0,100,0]: #BLUE
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions + :num_potions"), parameters= dict(num_potions = num_potions))
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - :num_ml"), parameters= dict(num_ml = num_ml))
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
        resources = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml FROM resources"))
        potions = connection.execute(sqlalchemy.text("SELECT name, inventory FROM potions"))
    
    resources = resources.first()
    red_ml = resources[0]
    green_ml = resources[1]
    blue_ml = resources[2]
    
    red_potions = red_ml // 100
    green_potions = green_ml // 100
    blue_potions = blue_ml // 100
    return [
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": red_potions,
                },
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": green_potions,
                },
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": blue_potions,
                }
            ]
    
