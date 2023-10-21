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
        potions_result = connection.execute(sqlalchemy.text("SELECT sku, name, inventory, price, red, green, blue, dark FROM potions WHERE inventory > 0")).all()
    
    catalog = []
    print("CATELOG: ")
    for row in potions_result:
        sku = row[0]
        name = row[1]
        inventory = row[2]
        price = row[3]
        red = row[4]
        green = row[5]
        blue = row[6]
        dark = row[7]

        print("----------------\n","sku: ", sku, 
              "\nname: ", name,
              "\ninventory: ", inventory,
              "\nprice: ", price, 
              "\npotion type: ", [red,green,blue,dark],
              "\n-----------------")
        
        item = {
                    "sku": sku,
                    "name": name,
                    "quantity": inventory,
                    "price": price,
                    "potion_type": [red,green,blue,dark],
                }
        if sku != "BLUE_POTION_0":
            catalog.append(item)

    return catalog
    