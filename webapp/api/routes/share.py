#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends, HTTPException
import json
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib

from .mysql import sql
from .functs import get_budgetid, check, get_timestamp,get_notisettings

from .sendmail import mail

from .admin import oauth2_scheme,get_current_user
share = APIRouter()

@share.post("/newshare")
async def newshare(budget_id: str, shareto: str, current_user = Depends(get_current_user)):
    mysql = sql()
    check(mysql,current_user["bid_mapping"], budget_id)

    name = current_user["name"].capitalize()
    userid = current_user["id"]

    query = '''select sharecode,name from pig_budgets where id="{}"'''.format(budget_id)

    query_data = mysql.get(query)

    sharecode = query_data[0]["sharecode"]
    budget_name = query_data[0]["name"]


    tmpuuid = uuid.uuid4()
    tmpuuid = str(tmpuuid) + sharecode
    tmphash = hashlib.sha256(str(tmpuuid).encode('utf-8')).hexdigest()

    uri = sharecode + "!" + tmphash

    set_timestamp = '''insert into pig_urlexpire(url,budget_id) values("{}","{}")'''.format(uri,budget_id)
    mysql.post(set_timestamp)

    payload = { "mode": "share", "hashed_url": uri, "budget": budget_name, "to_address": shareto, "user": name } 
    mailstate, code, message = mail(payload)

    notisettings = get_notisettings(mysql,shareto,"4","3")
    print(shareto, flush=True)

    if notisettings[0]["web"] == 1:
        noti_query = '''insert into pig_notifications (srcuid, budgetid,value,destuid,state,messageid,typeid) values ({},{},"{}",{},0,4,3)'''.format(userid,budget_id,budget_name,shareto)
        print(noti_query,flush=True)

        mysql.post(noti_query)
    mysql.close()

    if mailstate:
        return {"state": "Mail sent", "uri": uri }
        raise HTTPException(status_code=200, detail="OK")
    else:
        return {"state": "Mail not sent", "uri": uri }
        raise HTTPException(status_code=502, detail="Internal Server Error")

@share.post("/wanttoconn")
async def wanttoconn(sharecode: str, current_user = Depends(get_current_user)):
    bidmapping = current_user["bid_mapping"]

    mysql = sql()
    timestamp = '''select budget_id,timestamp from pig_urlexpire where url="{}"'''.format(sharecode)

    response = mysql.get(timestamp)

    if response == []:
        mysql.close()
        raise HTTPException(status_code=404, detail="Not found")

    timestamp = response[0]["timestamp"]

    budget_id = response[0]["budget_id"]

    print(get_timestamp(timestamp))

    if get_timestamp(timestamp):
        query = '''select b0,b1,b2,b3 from pig_bidmapping where id="{}"'''.format(bidmapping)
        response = mysql.get(query)

        for key,value in response[0].items():
            if not value:
                insert_budget_id = '''update pig_bidmapping set {} = {} where id={}'''.format(key,budget_id,bidmapping)
                mysql.post(insert_budget_id)
                delete_key = '''delete from pig_urlexpire where url="{}"'''.format(sharecode)
                mysql.post(delete_key)
                mysql.close()
                return HTTPException(status_code=200, detail="OK")
            else:
                continue
        else:
            mysql.close()
            return HTTPException(status_code=402, detail="Payment required")
    else:
        mysql.close()
        raise HTTPException(status_code=419, detail="Token expired")


@share.get("/budget_conns")
async def connect(budget_id: str, current_user = Depends(get_current_user)):
    mysql = sql()

    check(mysql,current_user["bid_mapping"], budget_id)

    query = '''select id,name,surname,email,(select sum(value) from pig_orders where user_id=id group by user_id)as value from registered_user where budget_id={} order by value DESC'''.format(budget_id)

    response = mysql.get(query)

    mysql.close()

    return response

@share.get("/availusers/{budget_id}", summary="Get all users")
async def users(budget_id: str, current_user = Depends(get_current_user)):

    mysql = sql()

    check(mysql,current_user["bid_mapping"], budget_id)
    user_id = current_user["id"]

    users_query = f'''select id,name,surname,email from registered_user where not id={user_id}'''

    try:
        response = mysql.get(users_query)

        print(response)

        mysql.close()

    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return response