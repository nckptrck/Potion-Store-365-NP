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


    with db.engine.begin() as connection:
        for potion in potions_delivered:

            num_potions = potion.quantity

            print("type: ", potion.potion_type, "\nquantity: ", potion.quantity, "\n--------")


            connection.execute(sqlalchemy.text(
                "INSERT INTO potion_inventory (potion_id, change) " 
                "SELECT id, :num_potions "
                "FROM potions " 
                "WHERE red = :red AND green = :green AND blue = :blue AND dark = :dark"),
                parameters= dict(num_potions = num_potions,
                                red = potion.potion_type[0],
                                green = potion.potion_type[1],
                                blue = potion.potion_type[2],
                                dark = potion.potion_type[3]))
            
            connection.execute(sqlalchemy.text(
                "INSERT INTO potion_ingredients (red_change, green_change, blue_change, dark_change) " 
                "VALUES (-:red, -:green, -:blue, -:dark)"),
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
        resources = connection.execute(sqlalchemy.text("SELECT SUM(red_change), SUM(green_change), SUM(blue_change),SUM(dark_change) FROM potion_ingredients")).first()
        potions = connection.execute(sqlalchemy.text(   "select potions.id, red, green, blue, dark, potions.name, SUM(change) as Inventory, potions.price "
                                                        "from potion_inventory "
                                                        "right join potions on potions.id = potion_inventory.potion_id "
                                                        "group by potions.id "
                                                        "order by Inventory "
                                                        "LIMIT 9")).all()
        
        potion_count = connection.execute(sqlalchemy.text("SELECT SUM(change) FROM potion_inventory")).first()
    
        if len(resources) >= 1:
            red_ml = resources[0]
            green_ml = resources[1]
            blue_ml = resources[2]
            dark_ml = resources[3]

        if len(potion_count) == 1:
            potion_count = potion_count[0]
    bottles = []
    for potion in potions:
            red = potion[1]
            green = potion[2]
            blue = potion[3]
            dark = potion[4]
            p_type = [red, green, blue, dark]
            if p_type == [0,0,75,25] or p_type == [7,7,7,79] or p_type == [0,50,0,50]:
                continue
            bottles.append({"potion_type": [red, green ,blue, dark], 
                            "quantity": 0})

    while potion_count <=289:
        print("red ml: ", red_ml, "\ngreen ml: ", green_ml, "\nblue ml: ", blue_ml, "\npotion count: ", potion_count)
        make_more = False
        for potion in potions:
            red = potion[1]
            green = potion[2]
            blue = potion[3]
            dark = potion[4]
            p_type = [red, green, blue, dark]
            if p_type == [0,0,75,25] or p_type == [7,7,7,79] or p_type == [0,50,0,50]:
                continue
            if red_ml >= red and green_ml >= green and blue_ml >= blue and dark_ml >= dark:
                make_more = True
                potion_count += 1
                red_ml -= red
                green_ml -= green
                blue_ml -= blue
                dark_ml -= dark
                for bottle in  bottles:
                    if bottle["potion_type"] == p_type:
                        print(p_type)
                        bottle["quantity"] += 1
                        print("quantity:", bottle["quantity"])
                        
            else:
                continue

        if not make_more:
            break
    
    print(potion_count)
    return bottles

# Bottler Ideas:

# for potion in

                


    
