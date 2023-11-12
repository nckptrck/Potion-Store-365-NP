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
        recent_sales = connection.execute(sqlalchemy.text(  "WITH recentsales as (  "
                                                            "SELECT potion_name, sum(quantity) as recentsales "
                                                            "FROM search_table "
                                                            "WHERE created_at >= now() - interval '2 hours' "
                                                            "GROUP BY potion_name), "

                                                            "inventory as ( "
                                                            "select potions.sku, potions.id, potions.name, SUM(change) as Inventory, potions.price, red, green, blue, dark "
                                                            "from potion_inventory "
                                                            "right join potions on potions.id = potion_inventory.potion_id "
                                                            "group by potions.id "
                                                            "order by Inventory desc) "

                                                            "SELECT sku, name, recentsales, inventory, price, red, green, blue, dark "
                                                            "FROM recentsales "
                                                            "LEFT JOIN inventory on inventory.name = recentsales.potion_name "
                                                            "WHERE recentsales > 3 "
                                                            "ORDER BY recentsales")).all()
        potions_inventory = connection.execute(sqlalchemy.text("SELECT sku, name, SUM(potion_inventory.change) as inventory, price, red, green, blue, dark "
                                                            "FROM potions LEFT JOIN potion_inventory on potions.id = potion_inventory.potion_id "
                                                            "GROUP BY sku, name, price, red, green, blue, dark "
                                                            "ORDER BY inventory DESC "
                                                            "LIMIT 6 "
                                                            )).all()
    
    catalog = []
    print("CATELOG: ")
    for row in recent_sales:
        sku = row[0]
        name = row[1]
        inventory = row[3]
        if inventory == 0:
            continue
        price = row[4]
        red = row[5]
        green = row[6]
        blue = row[7]
        dark = row[8]

        item = {
                    "sku": sku,
                    "name": name,
                    "quantity": inventory,
                    "price": price,
                    "potion_type": [red,green,blue,dark],
                }
     
        catalog.append(item)

    for row in potions_inventory:
        sku = row[0]
        name = row[1]
        inventory = row[2]
        if inventory == 0:
            continue
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
        if item not in catalog and len(catalog) < 6:
            catalog.append(item)

    return catalog
    