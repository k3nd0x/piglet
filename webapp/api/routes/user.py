#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: showmatch ts=4 sts=4 sw=4 autoindent smartindent smarttab expandtab

from fastapi import APIRouter, Path, Depends,status,HTTPException
from enum import Enum
import json
from pydantic import BaseModel, Field
from typing import Optional, Dict
import hashlib
from fastapi.responses import JSONResponse
import uuid

from .mysql import sql
from .sendmail import send_resetmail, send_verification
from .functs import hex_color, get_timestamp
from .admin import oauth2_scheme,get_current_user

user = APIRouter()

class registerUser(BaseModel):
    email: str
    password: str
    class Config:
        schema_extra = {
            "example": {
                "email": "app.app.de",
                "password": "hashed_salted_pw"
                }
            }

@user.post("/register_user")
async def register_user(registerUser: registerUser):
    mysql = sql()

    share_code = uuid.uuid4().hex
    query = '''insert into pig_budgets(mode,name,sharecode) values (0,"MyBudget","{}")'''.format(share_code)

    mysql.post(query,close=False)
    budget_id = mysql.lastrowid()

    query = '''insert into pig_bidmapping(b0) values ({})'''.format(budget_id)
    mysql.post(query,close=False)
    bid_mapping = mysql.lastrowid()


    email = str(registerUser.email)
    password = str(registerUser.password)
    hashed_mail = str(hashlib.sha256(email.encode()).hexdigest())
    shamail = hashed_mail[:15]


    color = hex_color()

    query = '''insert into registered_user( id, email,password,color, shamail,budget_id,bid_mapping ) select max( id ) + 1, "{}", "{}", "{}", "{}","{}","{}" from registered_user'''.format(email,password,color,shamail,budget_id,bid_mapping)

    return_value = mysql.post(query)

    if return_value == "duplicated":
        raise HTTPException(status_code=409, detail="User already exists")
    else:
        send_verification(email,hashed_mail)
        return_value = "added"

    mysql.close()

    return return_value

@user.get("/login-user")
async def login_user(current_user = Depends(get_current_user)):
    mysql = sql()
    print(current_user,flush=True)

    email = current_user["email"]

    query = '''select r.id,r.email,r.verified,r.name,r.surname,r.color,r.image,r.budget_id,r.bid_mapping,pig_bidmapping.b0,pig_bidmapping.b1,pig_bidmapping.b2,pig_bidmapping.b3 from registered_user as r join pig_bidmapping on pig_bidmapping.id = r.bid_mapping where r.email="{}"'''.format(email)


    response = mysql.get(query)
    print(response,flush=True)

    mysql.close()

    try:
        if response == []:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="NoSuchUser")
        else:
            return response[0]
    except:
        raise HTTPException(status_code=400, detail="Bad Request")

class updateUser(BaseModel):
    id: str
    image: str
    email: str
    name: str
    surname: str
    color: str
    class Config:
        schema_extra = {
            "example": {
                "id": "2",
                "image": "69c36c1.jpg",
                "email": "admin@admin.de",
                "name": "Admin",
                "surname": "Test",
                "color": "#123123"
                }
            }
@user.put("/update-user")
async def update_user(registerUser: updateUser,current_user = Depends(get_current_user)):
    mysql = sql()
    response = []

    if str(registerUser.id) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Forbidden")

    query = '''select image,id,email,name,surname,color from registered_user where id="{}"'''.format(registerUser.id)
    user_now = mysql.get(query)[0]


    if registerUser.name != "string":
        if user_now["name"] == registerUser.name:
            pass
        else:
            query = '''update registered_user set name="{}" where id="{}"'''.format(registerUser.name,registerUser.id)
            mysql.post(query)

    if registerUser.surname != "string":
        if user_now["surname"] == registerUser.surname:
            pass
        else:
            query = '''update registered_user set surname="{}" where id="{}"'''.format(registerUser.surname,registerUser.id)
            mysql.post(query)
    if registerUser.image != "string":
        if user_now["image"] == registerUser.image:
            pass
        else:
            query = '''update registered_user set image="{}" where id="{}"'''.format(registerUser.image,registerUser.id)
            mysql.post(query)

    if registerUser.email != "string":
        if user_now["email"] == registerUser.email:
            pass
        else:
            query = '''update registered_user set email="{}" where id="{}"'''.format(registerUser.email,registerUser.id)
            mysql.post(query)

    if registerUser.color != "string":
        if user_now["color"] == registerUser.color:
            pass
        else:
            query = '''update registered_user set color="{}" where id="{}"'''.format(registerUser.color,registerUser.id)
            mysql.post(query)

    query = '''select image,id, email, name, surname, color from registered_user where id="{}"'''.format(registerUser.id)
    response = mysql.get(query)[0]

    if user_now == response:
        response = {}
    else:
        response["old_image"] = user_now["image"]
        response = response


    mysql.close()
    return response

@user.delete("/account")
async def delete_account(userid: str,budget_id: str, force: bool=False, dict = Depends(oauth2_scheme)):
    mysql = sql()
    response = []

    if force == True:
        if mysql.get('''select mode from pig_budgets where id={}'''.format(budget_id))[0]["mode"] == 0:
            query = '''delete from pig_budgets where id={} and mode=0'''.format(budget_id)
            query1 = '''delete from pig_category where budget_id={}'''.format(budget_id)
            query2 = '''delete from pig_bidmapping where b0={}'''.format(budget_id)
            for i in query,query1,query2:
                response.append(mysql.delete(i))
        query = '''delete from new_orders where user_id={}'''.format(userid)
        query1 = '''delete from registered_user where id={}'''.format(userid)

        for i in query,query1:
            response.append(mysql.delete(i))


    elif force == False:
        query = '''select value from new_orders where user_id={}'''.format(userid)
        orders = mysql.get(query)
        if orders == []:
            mode = mysql.get('''select mode from pig_budgets where id={}'''.format(budget_id))
            if mode[0]["mode"] == 0:
                query = '''delete from pig_budgets where id={} and mode=0'''.format(budget_id)
                query1 = '''delete from pig_category where budget_id={}'''.format(budget_id)
                for i in query, query1:
                    response.append(mysql.delete(i))
            query = '''delete from registered_user where id={}'''.format(userid)
            response.append(mysql.delete(query))
        else:
            response.append("ORDERSnotEMPTY")

    mysql.close()
    if "Entity deleted" in response:
        return "DELuserOK"


def timestamp_set(email):
    tmpuuid = uuid.uuid4()
    tmpuuid = str(tmpuuid) + email
    tmphash = hashlib.sha256(str(tmpuuid).encode('utf-8')).hexdigest()

    return tmphash


@user.post("/forgot-request")
async def forgot_password(email: Optional[str]=None ,tmphash: Optional[str]=None):
    mysql = sql()
    if not email and not tmphash:
        return False,"AddParameters"

    elif email and not tmphash:
        query = '''select email,id from registered_user where email="{}"'''.format(email)

        user_available = mysql.get(query)

        if user_available == []:
            return False, "UserNotAvailable"
        else:
            query = '''select timestamp,email,hash from pig_pwforgot where email="{}"'''.format(email)
            current_state = mysql.get(query)

            if current_state == []:
                tmphash = timestamp_set(email)
                query = '''insert into pig_pwforgot(email, hash) values("{}", "{}")'''.format(email,tmphash)
                db_response = mysql.post(query)
                if db_response:
                    response = "timestampSetMailSent"
                    send_resetmail(email,tmphash)
                else:
                    response = "MYSQl Query failed"
                
                response = db_response, response
            
            elif current_state[0]["timestamp"]:
                db_timestamp = current_state[0]["timestamp"]

                if get_timestamp(db_timestamp):
                    tmphash = timestamp_set(email)
                    query = '''update pig_pwforgot set hash="{}" where email="{}"'''.format(tmphash,email)
                    mysql.post(query)
                    mysql.close()
                    send_resetmail(email,tmphash)
                    return True, "timestampSetMailSent"
                else:
                    mysql.close()
                    return False, "alreadyProvided"

            else:
                mysql.close()
                response = False, current_state[0]["timestamp"]

            mysql.close()
            return response
    elif tmphash and not email:
        query = '''select timestamp,email,hash from pig_pwforgot where hash="{}"'''.format(tmphash)
        current_state = mysql.get(query)
        mysql.close()

        if current_state == []:
            return False, "linkNotValid"
        elif current_state[0]["timestamp"]:
            db_timestamp = current_state[0]["timestamp"]
            if get_timestamp(db_timestamp):
                return False,"linkExpired"
            else:
                return True
    else:
        return False,"NotImplemented"

@user.put("/update-pw")
async def update_pw(passwordhash: str, tmphash: str):
    mysql = sql()

    email_query = '''select email from pig_pwforgot where hash="{}"'''.format(tmphash)

    email = mysql.get(email_query)[0]["email"]

    update_query = '''update registered_user set password="{}" where email="{}"'''.format(passwordhash,email)

    value = mysql.post(update_query)

    mysql.close()
    return value

@user.put("/confirm", summary="Used to send the verification mail (resend possible)")
async def confirm(hashed_mail: Optional[str]=None, send: Optional[bool]=False,current_user = Depends(get_current_user)):
    mysql = sql()

    email = current_user["email"]

    hashed_email = '''select shamail from registered_user where id={}'''.format(current_user["id"])

    hashed_email = mysql.get(hashed_email)

    hashed_email = hashed_email[0]["shamail"]

    if send:
        value = send_verification(email,hashed_email)

    elif not send and hashed_mail:
        update_user = '''update registered_user set verified=1 where shamail="{}"'''.format(hashed_mail[:15])
        value = mysql.post(update_user)


    mysql.close()
    return value
@user.get("/settings", summary="Get all settings of a user")
async def settings_get(current_user = Depends(get_current_user)):

    user_id = current_user["id"]

    mysql = sql()

    #get_settings = '''select (select name from pig_settings where id=setting_id) as setting, value from pig_usersettings where user_id={}'''.format(user_id)

    get_settings = '''select (select type from pig_notitype where id=notitype) as type, (select message from pig_notiobj where id=notiobj) as obj, mail, web from pig_notisettings where user_id={}'''.format(user_id)
    response = mysql.get(get_settings)

    return_response = []


    if response != []:
        for i in response:
            display_obj = '''select display from pig_notiobj where message="{}"'''.format(i["obj"])
            display_obj = mysql.get(display_obj)[0]["display"]

            display_type = '''select display from pig_notitype where type="{}"'''.format(i["type"])
            display_type = mysql.get(display_type)[0]["display"]

            #if i["type"] == "category":
            #    i_type = "Kategorie"
            #if i["obj"] == "added":
            #    i_obj = "hinzufügen"
            
            #if i["type"] == "order":
            #    i_type = "Geld"
            #if i["obj"] == "removed":
            #    i_obj = "entfernt"

                
            return_response.append({ i["type"] + "_" + i["obj"]: [{ "mail": i["mail"], "web": i["web"]}, {"display_name": "{} {}".format(display_type,display_obj)}]})
    else:
        return response

    mysql.close()
    return return_response

class patchSettings(BaseModel):
    settings: dict[str, dict[ str,str]]
@user.post("/settings", summary="Update user settings")
async def settings_patch(patchSettings: patchSettings, current_user = Depends(get_current_user)):
    mysql = sql()

    user_id = current_user["id"]

    return_list = []

    for value,key in patchSettings.settings.items():
        modes = value.split("_")

        noti_type = modes[0]
        noti_obj = modes[1]

        sql0 = '''select id from pig_notiobj where message="{}"'''.format(noti_obj)
        sql1 = '''select id from pig_notitype where type="{}"'''.format(noti_type)

        obj_id = mysql.get(sql0)[0]["id"]
        type_id = mysql.get(sql1)[0]["id"]

        try:
            mail = key["mail"]
        except:
            mail = 0

        try:
            web = key["web"]
        except:
            web = 0

        update_settings = '''update pig_notisettings set mail='{}', web='{}' where user_id="{}" and notiobj="{}" and notitype="{}"'''.format(mail,web,user_id,obj_id,type_id)

        return_data = mysql.post(update_settings)

        return_list.append(return_data)

    mysql.close()


    return return_list

    
