#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends,HTTPException
import json
from pydantic import BaseModel
from typing import Optional

from .mysql import sql

from .admin import oauth2_scheme,get_current_user

from .functs import check

import uuid

budget = APIRouter()

@budget.get("/")
async def _get(current_user = Depends(get_current_user),all: Optional[bool] = False):
    mysql = sql()
    if not all:
        query = f'''select pig_budgets.*, pig_userbudgets.joined from pig_budgets JOIN pig_userbudgets on pig_budgets.id = pig_userbudgets.budget_id where pig_userbudgets.user_id = {current_user["id"]} and pig_userbudgets.joined = 1 order by joined'''
    else:
        query = f'''select pig_budgets.*, pig_userbudgets.joined from pig_budgets JOIN pig_userbudgets on pig_budgets.id = pig_userbudgets.budget_id where pig_userbudgets.user_id = {current_user["id"]} order by joined'''
    response = mysql.get(query)
    mysql.close()

    return response

@budget.post("/add")
async def _add(name: str,currency: str, current_user = Depends(get_current_user)):
    mysql = sql()

    userid = current_user["id"]

    new_budget = None

    share_code = uuid.uuid4().hex

    query = '''insert into pig_budgets(mode,name,sharecode,currency) values (0,"{}","{}","{}")'''.format(name,share_code,currency)
    mysql.post(query,close=False)
    budget_id = mysql.lastrowid()

    #query = '''update pig_bidmapping set {}={} where id=(select bid_mapping from registered_user where id={})'''.format(new_budget,budget_id,userid)

    query = f'''insert into pig_userbudgets (user_id, budget_id,joined) values({userid},{budget_id},1)'''

    response = mysql.post(query)

    mysql.close()
    return response

@budget.put("/{budgetid}")
async def _update(budgetid: str, name:str, currency: str, current_user = Depends(get_current_user)):
    valid_currencies = [ "EUR", "USD", "GBP" ]
    if currency not in valid_currencies:
        raise HTTPException(status_code=403, detail="Forbidden - Try valid currency")

    mysql = sql()

    check(mysql,budgetid,current_user["id"])

    query = '''update pig_budgets set name="{}", currency="{}" where id={}'''.format(name,currency, budgetid)
    response = mysql.post(query)
    mysql.close()

    return response


@budget.post("/leave/{budgetid}")
async def _leave(budgetid: str, force: bool, current_user = Depends(get_current_user)):
    #### TOdo check if budget still used / orders in budget and so on
    mysql = sql()

    userid = current_user["id"]
    query = f'''select budget_id,user_id from pig_userbudgets where user_id = {userid}'''

    response = mysql.get(query)

    if len(response) > 1:
        query = f'''delete from pig_userbudgets where budget_id = {budgetid} and user_id = {userid}'''
        mysql.post(query)
        return True, "Budget left"
    else:
        return False, "You cannot leave your last budget"
