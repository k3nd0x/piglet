
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

    check(mysql,current_user["bid_mapping"], budget_id)

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
