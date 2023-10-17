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
        print("type: ", potion.potion_type, "\nquantity: ", potion.quantity, "\n--------")
    
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(
                "UPDATE potions " 
                "SET inventory = inventory + :num_potions " 
                "WHERE red = :red AND green = :green AND blue = :blue AND dark = :dark"),
                parameters= dict(num_potions = num_potions,
                                 red = potion.potion_type[0],
                                 green = potion.potion_type[1],
                                 blue = potion.potion_type[2],
                                 dark = potion.potion_type[3]))
            
            connection.execute(sqlalchemy.text(
                "UPDATE resources " 
                "SET red_ml = red_ml - :red, green_ml = green_ml - :green, blue_ml = blue_ml - :blue, dark_ml = dark_ml - :dark"),
                parameters=dict(red = (potion.potion_type[0] * num_potions),
                                green = (potion.potion_type[1] * num_potions),
                                blue = (potion.potion_type[2] * num_potions) ,
                                dark = (potion.potion_type[3] * num_potions))
                                )
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
        resources = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml FROM resources")).first()
        potions = connection.execute(sqlalchemy.text("SELECT name, red, green, blue, dark, inventory FROM potions")).all()
        min_red = connection.execute(sqlalchemy.text("SELECT MIN(red) FROM potions WHERE red > 0")).first()
        min_green = connection.execute(sqlalchemy.text("SELECT MIN(green) FROM potions WHERE green > 0")).first()
        min_blue = connection.execute(sqlalchemy.text("SELECT MIN(blue) FROM potions WHERE blue > 0")).first()
    
    red_ml = resources[0]
    green_ml = resources[1]
    blue_ml = resources[2]

    min_red = min_red[0]
    min_green = min_green[0]
    min_blue = min_blue[0]

    bottles = []
    for potion in potions:
            red = potion[1]
            green = potion[2]
            blue = potion[3]
            dark = potion[4]
            bottles.append({"potion_type": [red, green ,blue, dark], 
                            "quantity": 0})

    while red_ml >= min_red or green_ml >= min_green or blue_ml >= min_blue:
        print("red ml: ", red_ml, "\ngreen ml: ", green_ml, "\nblue ml: ", blue_ml)
        for potion in potions:
            red = potion[1]
            green = potion[2]
            blue = potion[3]
            dark = potion[4]
            p_type = [red, green, blue, dark]
            
            if red_ml >= red and green_ml >= green and blue_ml >= blue:
                red_ml -= red
                green_ml -= green
                blue_ml -= blue
                for bottle in  bottles:
                    if bottle["potion_type"] == p_type:
                        print(p_type)
                        bottle["quantity"] += 1
                        print("quantity:", bottle["quantity"])
            else:
                continue
        if (red_ml + blue_ml + green_ml) <= 100:
            break
    
    return bottles

                


    
