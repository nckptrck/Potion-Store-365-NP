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
    print("CREATING CART: ", "\nCart ID: ", index, "\nCustomer Name: ", new_cart.customer)
        
    return {"cart_id": index}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    with db.engine.begin() as connection:
        cart_data = connection.execute(sqlalchemy.text(
            "SELECT sku, quantity FROM cart_items JOIN potions on potions.id = cart_items.potion_id WHERE cart_items.cart_id = :cart_id"),
            parameters=(dict(cart_id = cart_id))).all()
    items = []
    for item in cart_data:
        items.append({"sku": item[0],
                      "quantity": item[1]})
    
    if len(items) == 0:
        items = None
    
    return {"cart_id": cart_id, "items": items}
    


class CartItem(BaseModel):
    quantity: int
    


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

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
    print("CHECKING OUT: ", "\n Cart ID: ", cart_id, "\nItems: ", get_cart(cart_id))
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO potion_inventory (potion_id, change) " 
                                           "SELECT potion_id, -cart_items.quantity "
                                           "FROM cart_items "
                                           "WHERE cart_items.cart_id = :cart_id"),
                                           parameters= dict(cart_id = cart_id))
        
        connection.execute(sqlalchemy.text("UPDATE customer_carts SET paid = TRUE WHERE id = :id"), 
                           parameters={"id": cart_id})
        
        connection.execute(sqlalchemy.text("INSERT INTO gold_ledger (change) " 
                                           "SELECT (subq.total_gold) "
                                           "FROM (SELECT cart_items.cart_id, SUM(potions.price * cart_items.quantity) as total_gold "
                                                 "FROM cart_items "
                                                 "JOIN potions ON potions.id = cart_items.potion_id "
                                                 "WHERE cart_items.cart_id = :cart_id "
                                                 "GROUP BY cart_items.cart_id) AS subq "
                                           ),
                                           parameters= dict(cart_id = cart_id))
        

    return {"success": True}