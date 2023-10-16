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
        resources = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, gold FROM resources")).first()
        potions = connection.execute(sqlalchemy.text("SELECT SUM(inventory) FROM potions")).first()
        
    total_ml = resources[0] + resources[1] + resources[2]
    gold = resources[3]
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
