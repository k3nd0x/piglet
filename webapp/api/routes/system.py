from fastapi_health import health
from fastapi import APIRouter, Path, Depends,HTTPException
from .admin import oauth2_scheme,get_current_user

from .mysql import sql

system = APIRouter()

def healthy_condition():
    return {"system": "online"}


def sick_condition():
    return False


system.add_api_route("/sys-health", health([healthy_condition, sick_condition]))

@system.get("/env-health")
async def db_state(current_user = Depends(get_current_user)):
    try:
        mysql = sql()
        query = 'select VERSION()'
        response = mysql.fetchone(query)
        if response:
            return { True: "DB online"}
        else:
            return { False: "DB not online"}
    except:
        return { False: "DB not online" }
