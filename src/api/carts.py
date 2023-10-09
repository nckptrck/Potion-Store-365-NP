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


@router.post("/")
def create_cart(new_cart: NewCart):
    cart_id = 1
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    red_potion_sku = "RED_POTION_0"
    
    return {"cart_id": cart_id, "items": [{"sku": red_potion_sku, "quantity": 1}]}
    


class CartItem(BaseModel):
    quantity: int
    sku: str


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    red_potion_sku = "RED_POTION_0"

    if cart_item.sku != red_potion_sku:
        raise HTTPException(status_code=400, detail="You can only add one red potion to your cart")

    if cart_item.quantity != 1:
        raise HTTPException(status_code=400, detail="You can only add one red potion to your cart")


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
