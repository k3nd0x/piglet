#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends,HTTPException
from enum import Enum
import json
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .mysql import sql
from .functs import get_budgetid,check,_get_uids,get_notisettings

from .admin import oauth2_scheme,get_current_user

futurespends = APIRouter()

@futurespends.get("/", summary="Get all future spends by userid or budget_id")
async def spends(budget_id: int, max_entries: Optional[int]=30, current_user = Depends(get_current_user)):
    mysql = sql()
    check(mysql,current_user["bid_mapping"], budget_id)

    query = '''select (select name from registered_user where id=user_id) as user, (select name from pig_category where id=category_id) as category, CONCAT(value,' ',currency) AS value, id, DATE_FORMAT(timestamp, '%Y-%m-%d') as timestamp,description FROM pig_futurespends where budget_id={} order by timestamp DESC'''.format(budget_id)
    response = mysql.get(query)

    max_count = 1
    return_list = []

    for i in response:
        if max_count <= max_entries:
            return_list.append(i)
            max_count += 1

    graphquery = f'''select MONTH(TIMESTAMP) as monthnumber, MONTHNAME(TIMESTAMP) as month, sum(value) as value, currency from pig_futurespends where budget_id={budget_id} group by month;'''
    response = mysql.get(graphquery)

    currentMonth = int(datetime.now().month)

    return_dict = { "orders": return_list, "monthlist": [], "valuelist": [], "colorlist": [] }

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    updated_data = []

    if len(response) == 0:
        for month_number, month_name in enumerate(months, start=1):
            updated_data.append({'monthnumber': month_number, 'month': month_name,'value': 0.0, 'currency': 'EUR'})
    else:
        existing_data = {entry['monthnumber']: entry for entry in response}

        for month_number, month_name in enumerate(months, start=1):
            if month_number in existing_data:
                updated_data.append(existing_data[month_number])
            else:
                updated_data.append({'monthnumber': month_number, 'month': month_name,
                                     'value': 0.0, 'currency': response[0]["currency"]})


    for i in updated_data:
        if i["monthnumber"] >= currentMonth:
            value = float(i['value'])
                
            return_dict["monthlist"].append(i["month"])
            return_dict["colorlist"].append('#2739ff')
            return_dict["valuelist"].append(value)


    mysql.close()
    return return_dict

class newSpend(BaseModel):
    value: str
    userid: int
    category: str
    description: Optional[str] = None
    budget_id: str
    timestamp: str
    class Config:
        schema_extra = {
            "example": {
                "userid": "1",
                "category": "2",
                "value": "123.02",
                "budget_id": "151",
                "description": "Einkaufen Kupsch (ptional)",
                "timestamp": "2023-06-28 10:00:00"
            }
        }

@futurespends.post("/new", summary="Place new order with payload")
async def spends(newSpend: newSpend,current_user = Depends(get_current_user)):
    try:
        value = float(newSpend.value)
        category = int(newSpend.category)
        userid = int(newSpend.userid)
        budget_id = int(newSpend.budget_id)
        description = newSpend.description
        timestamp = newSpend.timestamp
    except:
        raise HTTPException(status_code=422, detail="Variables not valid")
    mysql = sql()

    if userid != current_user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    check(mysql,current_user["bid_mapping"], budget_id)

    currency_query = f"select currency from pig_budgets where id={budget_id}"
    curr = mysql.get(currency_query)[0]["currency"]

    query = '''insert into pig_futurespends(value,currency,user_id,category_id,budget_id,description,timestamp) VALUES ({},"{}",{},{},{},"{}","{}")'''.format(value,curr,userid,category,budget_id,description,timestamp)
    insert = mysql.post(query)
    if insert == True:
        output = "Order added".format(userid,value, curr, category,description)


    mysql.close()
    return output
@futurespends.delete("/{id}", summary="Delete order by timestamp")
async def spends(id: str, budget_id: str,current_user = Depends(get_current_user)):
    mysql = sql()

    userid = current_user["id"]
    check(mysql,current_user["bid_mapping"], budget_id)

    query = '''delete from pig_futurespends where id="{}" and budget_id={}'''.format(id,budget_id)

    response = mysql.delete(query)

    mysql.close()

    return response
