from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

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
    global index
    index += 1
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            "INSERT INTO customer_carts (customer_name) VALUES (:customer_name)"), 
            parameters=(dict(customer_name = new_cart.customer)))
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
    sku: str


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        cart = connection.execute(sqlalchemy.text(
                "SELECT items FROM customer_carts WHERE id = :id"), 
                parameters=(dict(id = cart_id)))
    cart_data = cart.first()
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    
    items = cart_data[0]

    

    for item in items:
        if item["sku"] == item_sku:
            item["quantity"] = cart_item.quantity
            break
    else:
        items.append({"sku": item_sku, "quantity": cart_item.quantity})
    
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions - 1"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + 50"))

    return {"total_potions_bought": 1, "total_gold_paid": 50}
