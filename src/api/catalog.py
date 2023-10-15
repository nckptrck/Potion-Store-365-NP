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
        potions_result = connection.execute(sqlalchemy.text("SELECT sku, name, inventory, price, potion_type FROM potions WHERE inventory > 0")).all()
    
    catalog = []
    for row in potions_result:
        sku = row[0]
        name = row[1]
        inventory = row[2]
        price = row[3]
        potion_type = row[4]

        print("sku: ", sku, 
              "\nname: ", name,
              "\ninventory: ", inventory,
              "\nprice: ", price, 
              "\npotion type: ", potion_type)
        
        item = {
                    "sku": sku,
                    "name": name,
                    "quantity": inventory,
                    "price": price,
                    "potion_type": potion_type,
                }
        
        catalog.append(item)

    return catalog
    