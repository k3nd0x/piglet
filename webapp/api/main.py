#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab


from typing import Optional,Union
from fastapi import FastAPI, status, Request,HTTPException,Depends
from fastapi.responses import JSONResponse

tags_metadata = [
    {
        "name": "User",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Order",
        "description": "Place and delete orders",
    },
    {
        "name": "Category",
        "description": "Create,delete and change categories",
    },
    {
        "name": "Sharing",
        "description": "Share Budgets with other users",
    }
]

app = FastAPI(description="piglet-api", version="2.0",root_path="/api/v2", title="Piglet API",openapi_tags=tags_metadata)

from .routes.user import user
from .routes.order import order
from .routes.category import category
from .routes.share import share
from .routes.budget import budget
from .routes.reports import reports
from .routes.graph import graph 
from .routes.admin import admin
from .routes.notifications import notifications
from .routes.system import system
from .routes.futurespends import futurespends

app.include_router(user,prefix="/user",tags=["User"])
app.include_router(order,prefix="/order",tags=["Order"])
app.include_router(category,prefix="/category",tags=["Category"])
app.include_router(share,prefix="/share",tags=["Sharing"])
app.include_router(budget,prefix="/budget",tags=["Budget"])
app.include_router(reports,prefix="/reports",tags=["Report Generation"])
app.include_router(graph,prefix="/graph",tags=["Graph Generation"])
app.include_router(admin,prefix="/admin",tags=["Admin Part"])
app.include_router(notifications,prefix="/notifications",tags=["Notification generation and supplying"])
app.include_router(system,prefix="/system",tags=["Monitoring and Testing"])
app.include_router(futurespends,prefix="/futurespends",tags=["Future Spends orders"])
