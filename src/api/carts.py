from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from src.api import auth
import json
import sqlalchemy
from src import database as db
from enum import Enum

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    #with db.engine.connect() as connection:

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }



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
        
        connection.execute(sqlalchemy.text("INSERT INTO search_table (customer_name, potion_name, quantity) " 
                                           "SELECT customer_carts.customer_name, potions.name, cart_items.quantity "
                                           "FROM cart_items "
                                           "JOIN customer_carts on customer_carts.id = cart_items.cart_id "
                                           "JOIN potions on cart_items.potion_id = potions.id "
                                           "WHERE cart_items.cart_id = :cart_id"),
                                           parameters= dict(cart_id = cart_id))
        

    return {"success": True}