#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends,status, Request,HTTPException
from typing import Optional

from .mysql import sql
from .functs import has_numbers,check

from .admin import oauth2_scheme,get_current_user

reports = APIRouter()

@reports.get("/")
async def report(year: str, month: str, budget_id: int, current_user = Depends(get_current_user)):
    mysql = sql()

    check(mysql,current_user["bid_mapping"], budget_id)

    if has_numbers(month) == True:
        query = '''select (select name from registered_user where user_id=id) as user,value from pig_orders where MONTH(TIMESTAMP)= "{month}" and YEAR(TIMESTAMP) = "{year}" and budget_id="{budget_id}"'''.format(
                month=month,
                year=year,
                budget_id=budget_id
                )

        response = mysql.get(query)
    else:
        query = '''select (select name from registered_user where user_id=id) as user,value from pig_orders where MONTHNAME(TIMESTAMP) = "{month}" and YEAR(TIMESTAMP) = "{year}" and budget_id="{budget_id}"'''.format(
                month=month,
                year=year,
                budget_id=budget_id
                )
        response = mysql.get(query)

    if response == []:
        raise HTTPException(status_code=404, detail="Not found!")
    else:

        stats_month = {}
        return_dict = {}
        response_dict = {}
        user_count = 0.0
        last_return = {}

        for i in response:
            if i["user"] not in stats_month:
                stats_month[i["user"]] = i["value"]
            else:
                stats_month[i["user"]] += i["value"]

        lowest = min(stats_month, key=stats_month.get)

        lowest_value = stats_month[lowest]

        for key,value in stats_month.items():
            if key != lowest:
                diff_value = round(lowest_value - value,3)

                if diff_value == -0:
                    diff_value = 0.0

                response_dict[lowest] = round(diff_value  / 2,2)
                response_dict[key] = 0.0

        last_return["users"] = response_dict

        if has_numbers(month) == True:
            for i in mysql.get("""select name from months where id='%s'"""%(month)):
                i = i["name"]
                last_return["month"] = i
        else:
            month = month.capitalize()
            last_return["month"] = month

        mysql.close()

        return last_return

@reports.get("/months")
async def months(budget_id: str, current_user = Depends(get_current_user)):
    mysql = sql()

    check(mysql,current_user["bid_mapping"], budget_id)

    query = """select distinct YEAR(pig_orders.timestamp) as year, CONVERT(months.id, INT) as id, months.name from months inner join pig_orders on MONTHNAME(pig_orders.timestamp)=months.name where budget_id={}""".format(budget_id)

    response = mysql.get(query)
    #response = mysql.get("""select distinct CONVERT(YEAR(pig_orders.timestamp),CHAR(50)) as year where budget_id={} order by year desc""".format(budget_id))
    return_dict = {}

    year_list = []
    month_dict = []
    for i in response:
        if str(i["year"]) not in year_list:
            year_list.append(str(i["year"]))
        if {"id": i["id"], "name": i["name"]} not in month_dict:
            month_dict.append({"id": i["id"], "name": i["name"]})
    month_dict = sorted(month_dict, key=lambda d: d['id'])

    #for i in response:
    #    if i["year"] not in return_dict:
    #        return_dict[i["year"]] = []
    #    return_dict[i["year"]].append({ "id": i["id"], "name": i["name"]})
    mysql.close()


    return month_dict,year_list

