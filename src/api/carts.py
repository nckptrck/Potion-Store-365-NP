from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from src.api import auth
import json
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str


index = 0
@router.post("/")
def create_cart(new_cart: NewCart):

    with db.engine.begin() as connection:
        index = connection.execute(sqlalchemy.text(
            "INSERT INTO customer_carts (customer_name) VALUES (:customer_name) RETURNING id"), 
            parameters=(dict(customer_name = new_cart.customer)))
    
    index = index.scalar()
        
    return {"cart_id": index}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    with db.engine.begin() as connection:
        cart = connection.execute(sqlalchemy.text(
            "SELECT items FROM customer_carts WHERE id = :id"), 
            parameters=(dict(id = cart_id)))
    cart_data = cart.first()
    items = cart_data[0]

    return {"cart_id": cart_id, "items": items}
    


class CartItem(BaseModel):
    quantity: int
    


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("Cart ID:", cart_id)

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, quantity, potion_id) " 
                                        "SELECT :cart_id, :quantity, potions.id "
                                        "FROM potions WHERE potions.sku = :item_sku"),
                                        parameters= dict(cart_id = cart_id,
                                                         item_sku = item_sku,
                                                         quantity = cart_item.quantity))
        connection.commit()
    return "OK"



class CartCheckout(BaseModel):
    payment: str
    

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE potions " 
                                           "SET inventory = potions.inventory - cart_items.quantity "
                                           "FROM cart_items "
                                           "WHERE potions.id = cart_items.potion_id AND cart_items.cart_id = :cart_id"),
                                           parameters= dict(cart_id = cart_id))
        
        connection.execute(sqlalchemy.text("UPDATE customer_carts SET paid = TRUE WHERE id = :id"), 
                           parameters={"id": cart_id})
        
        connection.execute(sqlalchemy.text("UPDATE resources " 
                                           "SET gold = resources.gold + subq.total_gold "
                                           "FROM (SELECT cart_items.potion_id, SUM(potions.price * cart_items.quantity) as total_gold "
                                                 "FROM cart_items "
                                                 "JOIN potions ON potions.id = cart_items.potion_id "
                                                 "WHERE cart_items.cart_id = :cart_id "
                                                 "GROUP BY cart_items.potion_id) AS subq "
                                           ),
                                           parameters= dict(cart_id = cart_id))
        

    return {"success": True}

"""
        items_tuple = connection.execute(sqlalchemy.text("SELECT items from customer_carts WHERE id = :id"), 
                           parameters={"id": cart_id}).first()
        items = items_tuple[0]

        pot_inventory = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
        row = pot_inventory.first()

        red_potions = row[0]
        green_potions = row[1]
        blue_potions = row[2]

        total_gold = 0
        for item in items:
            sku = item.get("sku")
            quantity = item.get("quantity")
            if sku == "RED_POTION_0" and quantity <= red_potions:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions - :quant"),
                           parameters={"quant": quantity})
                total_gold += (50* quantity)
            elif sku == "GREEN_POTION_0" and quantity <= green_potions:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions - :quant"),
                           parameters={"quant": quantity})
                total_gold += (50* quantity)
            elif sku == "BLUE_POTION_0" and quantity <= blue_potions:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions - :quant"),
                           parameters={"quant": quantity})
                total_gold += (50* quantity)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid item in cart: SKU={sku}, Quantity={quantity}")



        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :paid"),
                           parameters={"paid": total_gold})
        
        connection.execute(sqlalchemy.text("UPDATE customer_carts SET paid = TRUE WHERE id = :id"), 
                           parameters={"id": cart_id})"""
    
