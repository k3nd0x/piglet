#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends,HTTPException
import json
from pydantic import BaseModel
from typing import Optional

from .mysql import sql
from .functs import get_budgetid,get_notisettings, hex_color,check,_get_uids

from .sendmail import mail

from .admin import oauth2_scheme,get_current_user

category = APIRouter()

@category.get("/{budget_id}", summary="Get all categories, or by budget_id")
async def categories(budget_id: int,current_user = Depends(get_current_user)):
    mysql = sql()

    check(mysql,budget_id,current_user["id"])

    query = '''select id,name,color from pig_category where displayed=1 and budget_id="{}"'''.format(budget_id)
    row = mysql.get(query)

    mysql.close()
    return row


@category.post("/", summary="Add new category")
async def categories(catname: str, color: str, budget_id: int, current_user = Depends(get_current_user)):
    mysql = sql()
    user_id = current_user["id"]

    check(mysql,budget_id,current_user["id"])

    #data = get("""select exists(select name from pig_category where name='%s')"""%(catname))
    query = '''select exists(select name from pig_category where name="{}" and budget_id="{}")'''.format(catname,budget_id)

    data = mysql.get(query)


    for i in data:
        for key,value in i.items():
            existing = value

    if existing == 0:
        color = "#" + color
        #color = hex_color()
        query = '''insert into pig_category( budget_id,name,displayed,user_id,color) values ({},"{}",{},"{}","{}")'''.format(budget_id,catname,1,user_id,color)
        response = mysql.post(query)

        cat_id = mysql.lastrowid()

        uid_list = _get_uids(mysql,budget_id)

        for dstuid in uid_list:
            dstuid = dstuid["id"]

            if dstuid != user_id:
                notisettings = get_notisettings(mysql,dstuid,"1","2")

                if notisettings[0]["web"] == 1:
                    noti_query = '''insert into pig_notifications (srcuid, budgetid, value, destuid, state,messageid,typeid) values ({},{},{},{},0,1,2)'''.format(user_id, budget_id, cat_id, dstuid)
                    mysql.post(noti_query)

                if notisettings[0]["mail"] == 1:
                    username = '''select name from registered_user where id={}'''.format(user_id)
                    budget_name = '''select name from pig_budgets where id={}'''.format(budget_id)
                    cat_name = '''select name from pig_category where id={}'''.format(cat_id)
                    email = '''select email from registered_user where id={}'''.format(dstuid)

                    username = mysql.get(username)[0]["name"]
                    budget_name = mysql.get(budget_name)[0]["name"]
                    email = mysql.get(email)[0]["email"]
                    cat_name = mysql.get(cat_name)[0]["name"]

                    value = '''{} added a new category '{}' to the budget {}!'''.format(username, cat_name, budget_name)

                    header = '''{} Added a new category!'''.format(username)
                    
                    payload = { "mode": "noti", "to_address": email, "value": value, "header": header }
                    mailstate, code, message = mail(payload)
                    if not mailstate:
                        print(code, message,flush=True)

    elif existing == 1:
        response = "Category already exists"
    else:
        response = "Query failed"

    mysql.close()

    return str(response)


@category.delete("/{catid}", summary="Delete category by id")
async def categories(budget_id: str, catid: str,current_user = Depends(get_current_user) ):
    mysql = sql()

    check(mysql,budget_id,current_user["id"])

    query = '''select id from pig_category where id="{}" and budget_id="{}"'''.format(catid,budget_id)

    response = mysql.get(query)

    if not response:
        raise HTTPException(status_code=403, detail="Forbidden")
    else:
        query = '''delete from pig_category where id="{}" and budget_id="{}"'''.format(catid,budget_id)

        response = mysql.delete(query)

        mysql.close()

        return response




@category.put("/{catid}", summary="Change name and color of category")
async def _update_category(budget_id: str, catid: str, name: Optional[str]=None, color: Optional[str]=None,current_user = Depends(get_current_user)):
    mysql = sql()

    check(mysql,budget_id,current_user["id"])

    if name and not color:
        query = '''update pig_category set name="{}" where id={} and budget_id={}'''.format(name,catid,budget_id)

    elif not name and color:
        color = '#' + color
        query = '''update pig_category set color="{}" where id={} and budget_id={}'''.format(color,catid,budget_id)

    elif name and color:
        color = '#' + color
        query = '''update pig_category set name="{}",color="{}" where id={} and budget_id={}'''.format(name,color,catid,budget_id)


    response = mysql.post(query)
    mysql.close()

    return response

