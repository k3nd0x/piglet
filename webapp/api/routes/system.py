#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends,status
from fastapi.responses import JSONResponse
from fastapi_health import health


import mysql.connector

system = APIRouter()

def healthy_condition():
    return {"system": "online"}


def sick_condition():
    return False


system.add_api_route("/sys-health", health([healthy_condition, sick_condition]))

@system.get("/env-health")
async def db_state():
    try:
        mydb = mysql.connector.connect(
            host="10.10.0.30",
            user="piglet",
            password="FLASK_budget2PW!",
            database="piglet"
        )
        cursor = mydb.cursor()
        cursor.execute('select VERSION()')
        results = cursor.fetchone()
        cursor.close()
        mydb.close()

        if results:
            return { True: "DB online"}
        else:
            return { False: "DB not online"}
    except:
        return { False: "DB not online" }
