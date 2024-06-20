
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Depends,HTTPException
from pydantic import BaseModel
from typing import Union
import os

from .mysql import sql
from .sqlite import sql3

admin = APIRouter()

from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta

from passlib.hash import sha256_crypt as sha256
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import hashlib
import time
import logging

from .functs import hex_color, random_name,random_image


@admin.on_event("startup")
async def startup_event():
    date = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print("{} - Starting Piglet API...".format(date),flush=True)
    admin_uid = None

    if os.environ.get("DOMAIN"):
        domain = os.environ.get("DOMAIN")
    else:
        domain = "localhost"


    while admin_uid is None:
        try:
            mysql = sql()

            admin_uid = mysql.get("select id from registered_user where id=1")
        except:
            time.sleep(15)

    name, surname = random_name()
    image,image_name = random_image()
    if image:
        image.save(f'app/views/pictures/{image_name}')

    inserts = [ """INSERT IGNORE INTO months VALUES (2,"February"),(3,"March"),(4,"April"),(5,"May"),(6,"June"),(7,"July"),(8,"August"),(9,"September"),(10,"October"),(11,"November"),(12,"December"),(1,"January")""",
            """INSERT IGNORE INTO pig_budgets VALUES (100,0,"Default",0,"3ec5d92868964bfbbf223ca88f379ee9","USD")""",
            f"""INSERT IGNORE INTO pig_category VALUES (1,"Groceries",1,1,100,"{hex_color()}")""",
            """INSERT IGNORE INTO pig_notitype VALUES (1,"order","Money"),(2,"category","Category"),(3,"budget","Budget")""",
            """INSERT IGNORE INTO pig_notiobj VALUES (1,'added','added'),(2,'removed','removed'),(3,'joined','joined'),(4,'shared','shared')""",
            f'''INSERT IGNORE INTO registered_user VALUES (1,"admin@{domain}",1,"864fd3978f508ef03a3e9c24aef43b639d7725c15e08eeaf961a9b81c3adc097:0b108f78bca548fa8fa2721e46d83150","{name}","{surname}","{image_name}",NULL,"{hex_color()}","7eb304283ead5f6",100,10000,1)''',
            """INSERT IGNORE into pig_userbudgets values (1,100,1)""",
    ]

    if not admin_uid:
        for i in inserts:
            try:
                mysql.post(i)
            except:
                continue

    
    update_inserts = []

    for i in update_inserts:
        try:
            mysql.post(i)
        except:
            continue
    try:
        version = mysql.get("""select value from pig_meta where `key` = 'version'""")[0]["value"]
        print(f"Piglet Schema Version: {version}",flush=True)
        sql_files = []
        version = float(version)

        if version >= 1.2:
            schema_directory = '/webapp/config/dbschema/update'
            for file in os.listdir(schema_directory):
                if file.endswith('.sql'):
                    sql_files.append(file)
            
            for new_version in sql_files:
                new_version_float = float(new_version.split('.sql')[0])

                if new_version_float > version:
                    with open(f'/webapp/config/dbschema/update/{new_version}','r') as file:
                        sql_commands = file.read()
                    commands = sql_commands.split(";")
                    for i in commands:
                        try:
                            mysql.post(i)
                        except Exception as e:
                            print(f'Error in db schema upgrade -> {new_version_float} - {e}')
                            continue

    except:
        with open('/webapp/config/dbschema/update/1.2.sql','r') as file:
            sql_commands = file.read()
        commands = sql_commands.split(";")

        for i in commands:
            try:
                mysql.post(i)
            except Exception as e:
                print(f'Error in db schema upgrade -> 1.2 {e}')
                continue

    #### migrate pig_bidmapping to pig_userbudgets
    try:
        user_data = mysql.get('''select * from registered_user''')
        bidmapping_data = mysql.get('''select * from pig_bidmapping''')

        insert_query = "INSERT INTO pig_userbudgets (user_id, budget_id, joined) VALUES (%s, %s, %s)"

        for user in user_data:
            for bidmapping in bidmapping_data:
                if bidmapping["id"] == user["bid_mapping"]:
                    for i in "b0", "b1", "b2", "b3":
                        if bidmapping[i]:
                            mysql.post(f'''insert into pig_userbudgets values ({user["id"]},{bidmapping[i]},1)''')
            
            noti_queries = "INSERT IGNORE INTO pig_notisettings VALUES ({user_id},1,1,1,1),({user_id},1,2,1,1),({user_id},2,1,1,1),({user_id},2,2,1,1),({user_id},3,3,1,1),({user_id},1,3,1,1),({user_id},2,3,1,1),({user_id},4,3,1,1)".format(user_id=user["id"])
            mysql.post(noti_queries)
    except:
        print("Skipping bid_mapping migration")

    mysql.close()




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
    mysql.close()

    if not user_dict:
        raise HTTPException(status_code=404, detail="Not found")
    else:
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
    user = mysql.get('''select id,email,name from registered_user where email="{}"'''.format(username))
    mysql.close()
    if user is None:
        raise credentials_exception
    
    return user[0]


@admin.get("/users")
async def get_user(dict = Depends(oauth2_scheme)):
    mysql = sql()

    query = '''select id,email,budget_id from registered_user'''
    budget_id = mysql.get(query)

    mysql.close()
    return budget_id
