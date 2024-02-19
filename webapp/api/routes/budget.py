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
async def _get(current_user = Depends(get_current_user)):
    mysql = sql()
    #query = '''select CONVERT(pig_budgets.id, CHAR(50)) as id, name,sharecode,currency from pig_budgets inner join pig_bidmapping on pig_bidmapping.b0 = pig_budgets.id or pig_bidmapping.b1 = pig_budgets.id or pig_bidmapping.b2 = pig_budgets.id or pig_bidmapping.b3 = pig_budgets.id where pig_bidmapping.id=(select bid_mapping from registered_user where id="{}")'''.format(current_user["id"])
    query = f'''select pig_budgets.*, pig_userbudgets.joined from pig_budgets JOIN pig_userbudgets on pig_budgets.id = pig_userbudgets.budget_id where pig_userbudgets.user_id = {current_user["id"]} order by joined'''
    response = mysql.get(query)

    mysql.close()
    return response

@budget.post("/add")
async def _add(name: str,currency: str, current_user = Depends(get_current_user)):
    mysql = sql()

    userid = current_user["id"]

    #query = '''select b0,b1,b2,b3 from pig_bidmapping where id=(select bid_mapping from registered_user where id={})'''.format(userid)

    #response = mysql.get(query)
    new_budget = None

    #for _k, _v in response[0].items():
    #    if _v == None:
    #        new_budget = _k
    #        break
    #    else:
    #        continue

    #if new_budget == None:
    #    return False, "No Free budget"

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



    #bid_mapping = current_user["bid_mapping"]

    #query = '''select b0,b1,b2,b3 from pig_bidmapping where id=(select bid_mapping from registered_user where id={})'''.format(userid)

    #empty = 0

    #for _k,_v in mysql.get(query)[0].items():

    #    if _v != None:
    #        empty += 1

    #if empty <= 1:
    #    return False, "You cannot leave your last budget"
    #else:
    #    query = '''update pig_bidmapping set b0=NULL where b0={budgetid} and id={bid}'''.format(budgetid=budgetid,bid=bid_mapping)
    #    query1 = '''update pig_bidmapping set b1=NULL where b1={budgetid} and id={bid}'''.format(budgetid=budgetid,bid=bid_mapping)
    #    query2 = '''update pig_bidmapping set b2=NULL where b2={budgetid} and id={bid}'''.format(budgetid=budgetid,bid=bid_mapping)
    #    query3 = '''update pig_bidmapping set b3=NULL where b3={budgetid} and id={bid}'''.format(budgetid=budgetid,bid=bid_mapping)
    #    
    #    response = []
    #    for i in query,query1,query2,query3:
    #        response.append(mysql.post(i))

    #    query = '''select mode from pig_budgets where id={budgetid}'''.format(budgetid=budgetid)

    #    response = mysql.get(query)

    #    mode = int(response[0]["mode"])

    #    if mode == 0:
    #        if force:
    #            query = '''delete from pig_budgets where id={}'''.format(budgetid)
    #            response = mysql.post(query)
    #            return True, "Budget deleted"
    #        else:
    #            query = '''select budget_id from pig_orders where budget_id={}'''.format(budgetid)
    #            if mysql.get(query) == []:
    #                query = '''select budget_id from pig_category where budget_id={}'''.format(budgetid)
    #                if mysql.get(query) == []:
    #                    query = '''delete from pig_budgets where id={}'''.format(budgetid)
    #                    response = mysql.post(query)
    #                    return True, "Budget deleted"
    #                else:
    #                    return False, "Categories still in budget"
    #            else:
    #                return False, "Orders still in budget"
    #    else:
    #        return True, "Budget in use"

    
