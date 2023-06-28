import requests
import json
def get_data_api(mode, data=None,debug=False,auth=None):
    baseurl = "http://127.0.0.1:8080/"
    headers = { "accept": "application/json" }

    def get(url, data=None,debug=False,auth=None):
        if data == None:
            if debug:
                print(url,flush=True)
            try:
                r = requests.get(url, headers=headers)
                response = r.json()
                if debug:
                    print(response,flush=True)
            except:
                response = [ 500 ]
        else:
            if debug:
                print(url,flush=True)
                print(data,flush=True)
            try:
                r = requests.get(url, headers=headers, data=json.dumps(data))
                response = r.json()
                if debug:
                    print(response,flush=True)
            except:
                response = [ 500 ]
        
        return response
    if mode == "orders":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "order/"

        budget_id = data["budget_id"]

        url = url + "?budget_id=" + str(budget_id)
        
        response = get(url)

        return response
    elif mode == "notis":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "notifications/"

        userid = str(data["uid"])

        if data["show_all"]:
            url = url + "?show_all=true"
        else:
            url = url + "?show_all=false"

        noticount, id_list, notifications = get(url)

        return noticount, id_list,notifications

    elif mode == "categorylist":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "category/"

        url = url + str(data)

        response = get(url)
        return response

    elif mode == "months":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "reports/months?budget_id={}".format(data)

        response = get(url)

        return response
    
    elif mode == "reports":
        headers["Authorization"] = "Bearer {}".format(auth)

        year = data["year"]
        month = data["month"]
        budget_id = data["budget_id"]
        url = baseurl + "reports/?year=" + year + "&month=" + month + "&budget_id=" + budget_id

        response2 = get(url)

        return response2
    
    elif mode == "login":
        email = data

        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "user/login-user"

        response = get(url)

        return response


    elif mode == "budgetmember":
        url = baseurl + "budget/member=budgetid={}".format(data)

        response = get(url)

        return response
    elif mode == "my_budgets":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "budget/"

        response = get(url)
        
        return response
    elif mode == "graph":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "graph/?budget_id={}".format(str(data))

        response = get(url)
        return response
    elif mode == "graph_report":
        headers["Authorization"] = "Bearer {}".format(auth)
        budget_id = data["budget_id"]
        year = data["year"]
        month = data["month"]
        url = baseurl + "graph/?budget_id={}&month={}&year={}".format(budget_id,month,year)

        response = get(url)
        return response
    elif mode == "settings":
        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "user/settings"

        response = get(url)

        return response
    elif mode == "futurespends":
        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "futurespends/"
        budget_id = data["budget_id"]

        url = url + "?budget_id=" + str(budget_id)
        
        response = get(url)

        return response
        
    
def post_data_api(mode, data,debug=False,auth=None):
    baseurl = "http://127.0.0.1:8080/"
    headers = { "accept": "application/json" }

    def post(url,auth=None):
        if debug:
            print(url,flush=True)
        try:
            r = requests.post(url, headers=headers, data=json.dumps(data))
            response = r.json()

            if debug:
                print(response,flush=True)
        except:
            response = [ 500 ]
        
        return response
    def put(url,auth=None):
        try:
            r = requests.put(url, headers=headers, data=json.dumps(data))
            response = r.json()
        except:
            response = [ 500 ]
        
        return response

    if mode == "orders":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "order/new"
        response = post(url)


    elif mode == "update-user":

        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "user/update-user"

        response = put(url)
    elif mode == "readNotis":
        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "notifications/read"

        response = post(url)


    elif mode == "categories":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "category/"

        new_cat = data["cat"]
        user_id = data["user_id"]
        budget_id = data["budget_id"]
        color = data["color"]
        if "#" in color:
            color = color.replace('#','')

        dataurl = "{}?catname={}&color={}&budget_id={}&user_id={}".format(url,new_cat,color,budget_id,user_id)

        response = post(dataurl)


    
    elif mode == "register":
        url = baseurl + "user/register_user"        
        print(url,flush=True)
        response = post(url)


    elif mode == "connect":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "share/wanttoconn"


        dataurl = "{}?sharecode={}".format(url, data)

        response = post(dataurl)
    
    #elif mode == "leave":
    #    url = baseurl + "share/leave"

    #    budget_id = data["budget_id"]
    #    user_id = data["user_id"]

    #   dataurl = "{}?budget_id={}&user_id={}".format(url,budget_id,user_id)

    #    response = post(dataurl)

    elif mode == "leave":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "budget/leave"

        budget_id = data["budget_id"]

        force = data["force"]

        dataurl = "{}/{}?force={}".format(url,budget_id,force)

        response = post(dataurl)

    elif mode == "forgot":
        url = baseurl + "user/forgot-request"

        if data["email"] != "":
            email = data["email"]
    
            dataurl = "{}?email={}".format(url,email)
        elif data["tmphash"] != "":
            tmphash = data["tmphash"]
            dataurl = "{}?tmphash={}".format(url,tmphash)

        response = post(dataurl)

    elif mode == "reset":
        url = baseurl + "user/update-pw"

        password = data["passwordhash"]
        tmphash = data["tmphash"]

        dataurl = "{}?passwordhash={}&tmphash={}".format(url, password, tmphash)

        response = put(dataurl)

    elif mode == "confirm":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "user/confirm"

        resend = data["send"]
        if not resend:
            hash_email = data["hashed_mail"]
            dataurl = "{}?hashed_mail={}&send={}".format(url,hash_email,resend)
        else:
            dataurl = "{}?send={}".format(url,resend)


        response = put(dataurl)

    elif mode == "newbudget":
        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "budget/add"

        user_id = data["user_id"]
        budget_name = data["name"]

        dataurl = "{}?name={}".format(url,budget_name)

        response = post(dataurl)
    elif mode == "ubudget":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "budget/"

        budget_id = data["id"]

        name = data["newname"]
        currency = data["newcurrency"]

        dataurl = "{}{}?name={}&currency={}".format(url,budget_id,name,currency)

        response = put(dataurl)

    elif mode == "uCat":

        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "category/"

        cat_id = data["id"]
        name = data["newname"]
        color = data["color"]
        budget_id = data["budget_id"]

        if color == "" and name != "":
            dataurl = "{}{}?budget_id={}&name={}".format(url,cat_id,budget_id,name)
            
        elif color != "" and name == "":
            if "#" in color:
                color = color.replace('#','')
            dataurl = "{}{}?budget_id={}&color={}".format(url,cat_id,budget_id,color)

        elif color != "" and name != "":
            if "#" in color:
                color = color.replace('#','')

            dataurl = "{}{}?budget_id={}&name={}&color={}".format(url,cat_id,budget_id,name,color)

        response = put(dataurl)
    
    elif mode == "sharewith":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "share/newshare"

        budget_id = data["budget_id"]
        shareto = data["shareto"]

        dataurl = "{}?budget_id={}&shareto={}".format(url,budget_id,shareto)

        response = post(dataurl)

    elif mode == "settings":
        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "user/settings"

        response = post(url)

    if mode == "futurespends":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "futurespends/new"
        response = post(url)



    return response

def del_data_api(mode, data,auth=None):
    baseurl = "http://127.0.0.1:8080/"
    headers = { "accept": "application/json" }

    def delete(url,auth=None):
        try:
            r = requests.delete(url, headers=headers, data=data)
            response = r.json()
        except:
            response = [ 500 ]
        
        return response
    
    if mode == "orders":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "order/"

        budget_id = data["budget_id"]
        ts = data["timestamp"]

        dataurl = "{}{}?budget_id={}".format(url,ts,budget_id)
        response = delete(dataurl)

        return response
#    elif mode == "users":
#        url = baseurl + "users"
#
#        dataurl = "{}?userid={}".format(url,data)
#        response = delete(dataurl)
#
#        return response
    elif mode == "categories":
        headers["Authorization"] = "Bearer {}".format(auth)
        url = baseurl + "category/"

        budget_id = data["budget_id"]
        cat_id = data["cat_id"]

        dataurl = "{}{}?budget_id={}".format(url,cat_id,budget_id)
        response = delete(dataurl)

        return response
    elif mode == "account":
        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "user/account"

        dataurl = "{}?userid={}&budget_id={}&force={}".format(url,data["user_id"],data["budget_id"], data["force"])

        response = delete(dataurl)

        return response
    elif mode == "futurespends":
        headers["Authorization"] = "Bearer {}".format(auth)

        url = baseurl + "futurespends/"

        dataurl = "{}{}?budget_id={}".format(url,data["id"],data["budget_id"])

        response = delete(dataurl)

        return response


def get_token(data):
    baseurl = "http://127.0.0.1:8080/"
    headers = { "accept": "application/x-www-form-urlencoded" }

    url = baseurl + "admin/token"
    user = data["email"]
    password = data["password"]

    data = { "username": user, "password": password}
    try:
        r = requests.post(url, headers=headers, data=data)
        response = r.json()
    except:
        response = [ 500 ]
    
    return response
