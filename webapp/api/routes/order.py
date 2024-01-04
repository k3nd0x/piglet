#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends,HTTPException, File, UploadFile
from enum import Enum
import json
from pydantic import BaseModel
from typing import Optional
from hashlib import md5
from pdfquery import PDFQuery

from .mysql import sql
from .functs import get_budgetid,check,_get_uids,get_notisettings
from .sendmail import mail

from .admin import oauth2_scheme,get_current_user
import csv
import uuid
from detect_delimiter import detect
import re

order = APIRouter()




@order.get("/", summary="Get all orders by userid or budget_id")
async def orders(budget_id: int, max_entries: Optional[int]=30, current_user = Depends(get_current_user)):
    mysql = sql()
    check(mysql,current_user["bid_mapping"], budget_id)

    query = '''select (select name from registered_user where id=user_id) as user, (select name from pig_category where id=category_id) as category, CONCAT(value,' ',currency) AS value, timestamp,description FROM new_orders where budget_id={} order by timestamp DESC'''.format(budget_id)
    response = mysql.get(query)

    max_count = 1
    return_list = []

    for i in response:
        if max_count <= max_entries:
            return_list.append(i)
            max_count += 1



    mysql.close()
    return return_list

class newOrder(BaseModel):
    value: str
    userid: str
    category: str
    description: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    budget_id: str
    class Config:
        schema_extra = {
            "example": {
                "userid": "1",
                "category": "2",
                "value": "123.02",
                "month": "04 (optional)",
                "year": "2022 (optional)",
                "budget_id": "151",
                "description": "Einkaufen Kupsch (optional)"
            }
        }

@order.post("/new", summary="Place new order with payload")
async def orders(newOrder: newOrder,current_user = Depends(get_current_user)):
    try:
        value = float(newOrder.value)
        category = int(newOrder.category)
        userid = int(newOrder.userid)
        budget_id = int(newOrder.budget_id)
        description = newOrder.description
    except:
        return "Variables not valid"
    mysql = sql()

    if userid != current_user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    check(mysql,current_user["bid_mapping"], budget_id)

    currency_query = f"select currency from pig_budgets where id={budget_id}"
    curr = mysql.get(currency_query)[0]["currency"]


    if newOrder.month != None and newOrder.year != None:
        year = newOrder.year
        month = newOrder.month
        date = "{}-{}-01 00:00:00".format(year,month)
        value = float(value)
        value = value + value

        value = str(value)

        query = """INSERT INTO new_orders (timestamp,value,currency,user_id,category_id,budget_id,description) VALUES ('%s','%s','%s',%s,%s,%s,'%s')"""%(date,value,curr,userid,category,budget_id,description)
        insert = mysql.post(query)
    else:
        query = '''insert into new_orders(value,currency,user_id,category_id,budget_id,description) VALUES ({},"{}",{},{},{},"{}")'''.format(value,curr,userid,category,budget_id,description)
        insert = mysql.post(query)

    if insert == True:
        output = "Order added".format(userid,value, curr, category,description)

        # 2022-07-04 Update MYSQL nötig - keine ids in new_order verfügbar
        #get_lastinsert = '''select id from new_orders where user_id={} order by timestamp DESC limit 1'''.format(userid)

        #lastinsert = get(get_lastinsert)[0]["id"]


        uid_list = _get_uids(mysql,budget_id)

        for dstuid in uid_list:
            dstuid = dstuid["id"]

            if dstuid != userid:

                notisettings = get_notisettings(mysql,dstuid,"1","1")

                if notisettings[0]["web"] == 1:
                
                    noti_query = '''insert into pig_notifications (srcuid, budgetid,value,destuid,state,messageid,typeid) values ({},{},{},{},0,1,1)'''.format(userid,budget_id,value,dstuid)

                    mysql.post(noti_query)

                try:
                
                    if notisettings[0]["mail"] == 1:
                        username = '''select name from registered_user where id={}'''.format(userid)
                        budget_name = '''select name,currency from pig_budgets where id={}'''.format(budget_id)
                        email = '''select email from registered_user where id={}'''.format(dstuid)

                        username = mysql.get(username)[0]["name"]
                        budget =  mysql.get(budget_name)[0]
                        budget_name = budget["name"]
                        budget_currency = budget["currency"]
                        email = mysql.get(email)[0]["email"]

                        mailvalue = '''{} added {} {} to the budget {}'''.format(username, value,currency, budget_name)

                        header = '''{} went shopping!'''.format(username)
                        
                        payload = { "mode": "noti", "to_address": email, "value": mailvalue, "header": header }
                        mailstate, code, message = mail(payload)
                        if not mailstate:
                            print(code, message,flush=True)
                except:
                    print("Error sending mail - check your mailserver config",flush=True)
    else:
        output = "Query failed - try again later"

    mysql.close()
    return output


@order.post('/uploadfile')
async def upload(file: UploadFile,budget_id: str, current_user = Depends(get_current_user)):
    mysql = sql()

    userid = current_user["id"]
    check(mysql,current_user["bid_mapping"], budget_id)

    filename = file.filename
    if "." in filename:
        filename = filename.split(".")
        extention = filename[1]
        filename = filename[0]
    random = uuid.uuid4()

    hashed_filename = md5(f"{filename}_{current_user['id']}_{random}".encode('utf-8')).hexdigest() + "." + extention
    upload_dir = f"api/uploads/{hashed_filename}"

    date_matcher = [ "datum", "date", "timestamp"]
    dest_matcher = [ "empfaenger"]

    if extention == "csv":
        def fix_nulls(s):
            for line in s:
                yield line.replace('\0', '')
        
        def normalize_key(input_key):
            input_key = str(input_key.lower())
            date_list = [ "date","datum", "timestamp"]
            value_list = [ 'value','betrag']
            usage_list = [ 'description','verwendungszweck' ]


        with open(upload_dir, "wb") as f:
            firstline = file.file.readline().decode('utf-8').strip('\n')
            f.write(file.file.read())
        data_dict_list = []

        delimiter = detect(firstline)

        if delimiter in firstline:
            firstline = firstline.split(delimiter)

            for i in firstline:
                normalized_key = normalize_key(i)
                if normalized_key:
                    print(normalized_key,flush=True)


        data_dict_list.append(firstline)

        with open(upload_dir, 'r', newline='', errors='replace', encoding='utf-8') as file:
            reader = csv.reader(fix_nulls(file), delimiter=delimiter)

            for row in reader:
                data_dict_list.append(row)
 
    return { 'file': data_dict_list } 


@order.delete("/{timestamp}", summary="Delete order by timestamp")
async def orders(timestamp: str, budget_id: str,current_user = Depends(get_current_user)):
    mysql = sql()

    userid = current_user["id"]
    check(mysql,current_user["bid_mapping"], budget_id)

    query = '''delete from new_orders where timestamp="{}" and budget_id={}'''.format(timestamp,budget_id,userid)

    response = mysql.delete(query)

    mysql.close()

    return response
