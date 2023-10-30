from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("DELETE FROM potion_inventory"))
        connection.execute(sqlalchemy.text("DELETE FROM potion_ingredients"))
        connection.execute(sqlalchemy.text("DELETE FROM gold_ledger"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_items"))
        connection.execute(sqlalchemy.text("DELETE FROM customer_carts"))
        connection.execute(sqlalchemy.text("INSERT INTO gold_ledger (change) VALUES (100)"))

    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Campus Bottle Speakeasy",
        "shop_owner": "Nick Patrick",
    }

