from fastapi import APIRouter
import json
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    with db.engine.begin() as connection:
        potions_result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
        row = potions_result.first()
        
    red_potions = row[0]
    green_potions = row[1]
    blue_potions = row[2]

    catalog = []

    
    if red_potions > 0:
        red = {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": red_potions,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                }
        catalog.append(red)
    elif green_potions >0:
        green = {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": green_potions,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }
        catalog.append(green)
    elif blue_potions >0:
        blue = {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": blue_potions,
                    "price": 50,
                    "potion_type": [0, 0, 100, 0],
                }
        catalog.append(blue)
    

    return catalog
    