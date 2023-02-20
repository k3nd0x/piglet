
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Depends,HTTPException
from pydantic import BaseModel
from typing import Union
import os

from .mysql import sql

admin = APIRouter()

from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta

from passlib.hash import sha256_crypt as sha256
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import hashlib
import time


@admin.on_event("startup")
async def startup_event():
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%s")
    print("{} - Starting Piglet API...".format(date))
    admin_uid = None
    while admin_uid is None:
        try:
            mysql = sql()

            admin_uid = mysql.get("select id from registered_user where id=1")
        except:
            time.sleep(15)

    if os.environ.get("DOMAIN"):
        domain = os.environ.get("DOMAIN")
    else:
        domain = "local"

    inserts = [ """INSERT INTO months VALUES (2,"February"),(3,"March"),(4,"April"),(5,"May"),(6,"June"),(7,"July"),(8,"August"),(9,"September"),(10,"October"),(11,"November"),(12,"December"),(1,"January")""",
            """INSERT INTO pig_bidmapping VALUES (10000,100,NULL,NULL,NULL)""",
            """INSERT INTO pig_budgets VALUES (100,0,"Default",0,"3ec5d92868964bfbbf223ca88f379ee9")""",
            """INSERT INTO pig_category VALUES (1,"Groceries",1,1,100,"#123456")""","""INSERT INTO "pig_notiobj" VALUES (1,"added","hinzufügen"),(2,"removed","entfernen"),(3,"joined","Beitritt")""",
            """INSERT INTO pig_notisettings VALUES (1,1,1,1,1),(1,1,2,1,1),(1,2,1,1,1),(1,2,2,1,1)""",
            """INSERT INTO pig_notitype VALUES (1,"order","Money"),(2,"category","Category"),(3,"budget","Budget")""",
            """INSERT INTO pig_notiobj VALUES (1,'added','added'),(2,'removed','removed'),(3,'joined','joined')""",
            '''INSERT INTO registered_user VALUES (1,"admin@{}",1,"864fd3978f508ef03a3e9c24aef43b639d7725c15e08eeaf961a9b81c3adc097:0b108f78bca548fa8fa2721e46d83150","admin","admin","default.png",NULL,"#8a40d0","7eb304283ead5f6",100,10000,1)'''.format(domain)]

    if not admin_uid:
        for i in inserts:
            try:
                mysql.post(i)
            except:
                continue
#@admin.on_event("shutdown"):
#async def shutdown_event():
#    print("Stopping Piglet API v2.1")
#    mysql.close()


### AUTHENTICATION ###
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="./admin/token")

SECRET_KEY = "ffc0d0f976851f91bdeed239e7131b164fe0e02c553571efd6eddd3cf42995a6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@admin.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    mysql = sql()
    query = '''select email,password from registered_user where email="{}"'''.format(form_data.username)
    user_dict = mysql.get(query)

    if not user_dict:
        mysql.close()
        raise HTTPException(status_code=404, detail="Not found")
    else:
        mysql.close()
        password = user_dict[0]["password"]
        user = user_dict[0]["email"]

        _hashed, salt = password.split(':')
        password_to_check = hashlib.sha256(salt.encode() + form_data.password.encode()).hexdigest()

        if _hashed == password_to_check:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=400, detail="Bad Request")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    mysql = sql()
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            mysql.close()
            raise credentials_exception
    except JWTError:
        mysql.close()
        raise credentials_exception
    user = mysql.get('''select id,email,name,bid_mapping from registered_user where email="{}"'''.format(username))
    if user is None:
        raise credentials_exception
    
    mysql.close()
    return user[0]


#@admin.delete("/{userid}")
#async def del_user(userid: int):
#    mysql = sql()
#
#    query = '''delete from registered_user where id={}'''.format(userid)
#
#    response = mysql.post(query)
#
#    mysql.close()
#
#    return response

@admin.get("/users")
async def get_user(dict = Depends(oauth2_scheme)):
    mysql = sql()

    #query = '''select id,email from registered_user'''

    query = '''select id,email,budget_id from registered_user'''


    budget_id = mysql.get(query)

    mysql.close()
    return budget_id
