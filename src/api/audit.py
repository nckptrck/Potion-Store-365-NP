from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        resources = connection.execute(sqlalchemy.text("SELECT SUM(red_change), SUM(green_change), SUM(blue_change), SUM(dark_change) FROM potion_ingredients")).first()
        gold = connection.execute(sqlalchemy.text("SELECT SUM(change) FROM gold_ledger")).first()
        potions = connection.execute(sqlalchemy.text("SELECT SUM(change) FROM potion_inventory")).first()
        
        for resource in resources:
            total_ml += resource
        gold = gold[0]
        if len(potions) == 1:
            total_potions = potions[0]


        
    return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
