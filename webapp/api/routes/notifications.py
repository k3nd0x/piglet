#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends, HTTPException
import json
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .mysql import sql
from .functs import get_budgetid,hex_color

from .admin import oauth2_scheme,get_current_user

notifications = APIRouter()

@notifications.get("/", summary="Get all notificatins which a relevant for this user")
async def notification(show_all: Optional[bool] = False, current_user = Depends(get_current_user)):
    mysql = sql()

    uid = str(current_user["id"])
    if show_all:
        query = '''select id, (select name from registered_user where id=srcuid) as srcname, (select name from pig_budgets where id=budgetid) as budget,state,(select currency from pig_budgets where id=budgetid) as currency,(select message from pig_notiobj where id=messageid) as message ,value, (select type from pig_notitype where id=typeid) as type ,timestamp from pig_notifications where destuid={} order by timestamp desc'''.format(uid)
    else:
        query = '''select id, (select name from registered_user where id=srcuid) as srcname, (select name from pig_budgets where id=budgetid) as budget,state,(select currency from pig_budgets where id=budgetid) as currency, (select message from pig_notiobj where id=messageid) as message ,value, (select type from pig_notitype where id=typeid) as type ,timestamp from pig_notifications where destuid={} and state=0 order by timestamp desc'''.format(uid)

    response = {}
    len_response = 0
    row = mysql.get(query)

    id_list = []


    for entry in row:

        if entry["srcname"] == None:
            srcname = current_user["email"]
        else:
            srcname = entry["srcname"]
        if entry["type"] == "order":
            if entry["message"] == "added":
                id_list.append(str(entry["id"]))
                message = "{} added {}{}  to the budget {}".format(srcname, entry["value"],entry["currency"], entry["budget"])

        elif entry["type"] == "category":
            if entry["message"] == "added":
                id_list.append(str(entry["id"]))
                message = "{} added a new category {}".format(srcname, entry["budget"])

        timestamp = entry["timestamp"]

        timestamp = timestamp.strftime("%d.%m.%Y, %H:%M:%S")

        response[timestamp] = message
        len_response = len(response)

        if len_response > 9:
            len_response = "9+"
        else:
            len_response = str(len_response)

    id_list = ",".join(id_list)

    mysql.close()

    return len_response,id_list, response

class readNotis(BaseModel):
    uid: str
    notilist: list
    class Config:
        schema_extra = {
            "example": {
                "uid": "2",
                "notilist": [ "1","2" ]
                }
            }


@notifications.post("/read", summary="Read all notifications per user")
async def notification_read(readNotis: readNotis, current_user = Depends(get_current_user)):
    mysql = sql()

    if readNotis.uid != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Forbidden")

    return_list = []

    for nid in readNotis.notilist:
        query = "update pig_notifications set state=1 where id={} and state=0 and destuid={}".format(nid,readNotis.uid)
        data = mysql.post(query)
        return_list.append(data)

    mysql.close()
    return return_list
