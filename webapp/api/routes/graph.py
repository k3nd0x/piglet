
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends
import json
from pydantic import BaseModel
from typing import Optional

from .mysql import sql
from .functs import has_numbers,get_budgetid,check

from .admin import oauth2_scheme,get_current_user

graph = APIRouter()
@graph.get("/")
async def _get(budget_id: str,month: Optional[str] = None, year: Optional[str]=None,current_user = Depends(get_current_user)):
    mysql = sql()
    timestamps = {}

    check(mysql,budget_id,current_user["id"])

    from calendar import monthrange
    from datetime import datetime

    return_dict = {}

    if year and month:
        if has_numbers(month) == False:
            month = month.lower()
            query = """select id from months where name='%s'"""%(month)

            month = mysql.get(query)[0]["id"]

        monthrange = monthrange(int(year), int(month))
        length_month = monthrange[1]

    else:
        month = datetime.now().month
        year = datetime.now().year

        monthrange = monthrange(int(year), int(month))
        length_month = monthrange[1]

    mfrom = "01." + str(month) + "." + str(year) + " 00:00:00"
    mto = str(length_month) + "." + str(month) + "." + str(year) + " 23:59:59"

    mfrom_ms = datetime.strptime(mfrom,'%d.%m.%Y %H:%M:%S')
    mfrom_ms = str(mfrom_ms.timestamp())

    mto_ms = datetime.strptime(mto,'%d.%m.%Y %H:%M:%S')
    mto_ms = str(mto_ms.timestamp())


    time_from = str(mfrom_ms)
    time_to = str(mto_ms)

    query = '''select (select name from registered_user where id=user_id) as user, (select color from registered_user where id=user_id) as color, sum(value) as value, currency from pig_orders where budget_id={} and timestamp between FROM_UNIXTIME({}) and FROM_UNIXTIME({}) group by user order by user'''.format(budget_id,time_from,time_to)

    user = mysql.get(query)

    return_dict["user"] = { "name": [], "color": [], "value": [] }
    return_dict["cat"] = { "name": [], "color": [], "value": [] }

    for i in user:
        return_dict["user"]["name"].append(i["user"])
        return_dict["user"]["color"].append(str(i["color"]))
        return_dict["user"]["value"].append(str(i["value"]))

    query = '''select sum(value) as value, (select name from pig_category where id=category_id) as name,(select color from pig_category where id=category_id) as color from pig_orders where timestamp between FROM_UNIXTIME({}) and FROM_UNIXTIME({}) and budget_id={} GROUP BY name order by name'''.format(time_from,time_to,budget_id)

    category = mysql.get(query)

    for i in category:
        return_dict["cat"]["name"].append(i["name"])
        return_dict["cat"]["color"].append(str(i["color"]))
        return_dict["cat"]["value"].append(str(i["value"]))

    mysql.close()
    return return_dict

@graph.get("/compare")
async def compare(budget_id: str,year1: int,year2:int, current_user = Depends(get_current_user)):
    try:
        mysql = sql()

        check(mysql,budget_id,current_user["id"])

        def get_data(year):
            query = f'''
            WITH AllCombinations AS (
        SELECT
            m.year,
            m.month,
            c.name,
            c.color
        FROM (
            SELECT DISTINCT
                YEAR(po.timestamp) AS year,
                MONTH(po.timestamp) AS month
            FROM pig_orders po
            WHERE YEAR(po.timestamp) = {year} AND po.budget_id = {budget_id}
        ) m
        CROSS JOIN (
            SELECT DISTINCT
                pc.name,
                pc.color
            FROM pig_category pc
            JOIN pig_orders po ON po.category_id = pc.id
            WHERE po.budget_id = {budget_id}
        ) c
    ),
    OrdersSummary AS (
        SELECT
            YEAR(po.timestamp) AS year,
            MONTH(po.timestamp) AS month,
            SUM(po.value) AS value,
            pc.name,
            pc.color
        FROM pig_orders po
        JOIN pig_category pc ON po.category_id = pc.id
        WHERE YEAR(po.timestamp) = {year} AND po.budget_id = {budget_id}
        GROUP BY YEAR(po.timestamp), MONTH(po.timestamp), pc.name, pc.color
    )
    SELECT
        ac.year,
        ac.month,
        COALESCE(os.value, 0) AS value,
        ac.name,
        ac.color
    FROM AllCombinations ac
    LEFT JOIN OrdersSummary os
    ON ac.year = os.year AND ac.month = os.month AND ac.name = os.name AND ac.color = os.color
    ORDER BY ac.year, ac.month, ac.name
    '''
            data = mysql.get(query)

            return data

        graph_data = []
        for year in [year1, year2]:
            if year == year1:
                stack = 'Stack 0'
            elif year == year2:
                stack = 'Stack 1'
            data = get_data(year)

            helper_dict = {}

            for i in data:
                if i["name"] not in helper_dict:
                    helper_dict[i["name"]] = []

                helper_dict[i["name"]].append(i["value"])

            processed = []
            for i in data:
                if i["name"] not in processed:
                    graph_data.append({
                        "label": i["name"],
                        "backgroundColor": i["color"], 
                        "data": helper_dict[i["name"]],
                        "stack": stack
                    })
                    processed.append(i["name"])

        mysql.close()
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return graph_data

# select (select name from pig_category where id=category_id) as category, round(avg(value),2) as avg_value from pig_orders where budget_id='100' and YEAR(timestamp)=2024 group by category_id;

@graph.get('/average')
async def avg(budget_id: str,year: int, mode: str, current_user = Depends(get_current_user)):
    mysql = sql()

    check(mysql,budget_id,current_user["id"])

    try:
        if mode == "category_spending":
            query = f'''SELECT 
        c.name AS label, 
        c.color as backgroundColor,
        ROUND(AVG(o.value), 2) AS data
    FROM 
        pig_orders o
    JOIN 
        pig_category c ON o.category_id = c.id
    WHERE 
        o.budget_id = '{budget_id}' 
        AND YEAR(o.timestamp) = {year}
    GROUP BY 
        c.name'''

        data = mysql.get(query)
    
        mysql.close()   
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return data