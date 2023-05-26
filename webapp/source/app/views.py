from cgitb import text
from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory
from source.app import app
from werkzeug.utils import secure_filename
from hashlib import sha256
import os
import json

from .api_func import get_data_api, post_data_api, del_data_api

def allowed_exts(ext):
    allowed = [ 'jpeg', 'jpg', 'png']
    ext = ext.lower()
    if ext in allowed:
        return True
    else:
        return False

def auth():
    auth = session["authorization"]

    return auth

def get_notis():
    userid = session["userid"]
    noticount, notilist, notifications = get_data_api("notis", data={ "uid": userid, "show_all": False},auth=auth())

    return noticount, notilist, notifications

# Neue Order hinzufügen /new-order
@app.route('/new-order', methods=["GET", "POST"])
def get_data():
    if session:
        session["title"] = "order"
        bid = session["budget_id"]
        userid = session["userid"]
        noticount, notilist, notifications = get_notis()
        if request.method == "POST":
            data = request.form.to_dict()
            data["budget_id"] = session["budget_id"]

            categorylist = get_data_api("categorylist",data=userid,auth=auth())

            response = post_data_api("orders", data,auth=auth())

            if response == "Order added!":
                flash_message = {response: "success"}
            else:
                flash_message = {response: "danger"}

            flash(flash_message)

            return redirect(url_for('get_data'))

        elif request.method == "GET":
            categorylist = get_data_api("categorylist",data=bid,auth=auth())

            return render_template("new-order.html", categorylist=categorylist,notifications=notifications, notilist=notilist, noticount=noticount)
    else:
        return redirect(url_for('login'))

# Default Index
@app.route('/', methods=["GET"])
def overview():
    if session:
        userid = session["userid"]
        budget_id = session["budget_id"]

        data = { "budget_id": budget_id}
        if request.method == "GET":
            orderlist = get_data_api("orders", data=data,auth=auth())
            session["title"] = "dashboard"

            noticount, notilist, notifications = get_notis()

            graphdata = get_data_api("graph", budget_id, auth=auth())

            return render_template("index.html", orderlist=orderlist,graphdata=graphdata,notifications=notifications, notilist=notilist, noticount=noticount )
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Settings Site 
@app.route('/settings', methods=["GET", "POST"])
def settings():
    if session:
        session["title"] = "settings"
        noticount, notilist, notifications = get_notis()
        noti_settings = get_data_api("settings", auth=auth())
        if request.method == "GET":
            return render_template("new_settings.html", noti_settings=noti_settings, notifications=notifications, notilist=notilist, noticount=noticount)
            
        elif request.method == "POST":

            payload = request.form.to_dict()
            if "name" in payload:
                if request.files['image'].filename != '':
                    file = request.files['image']
                    filename = file.filename
                    value  = filename.split('.')
                    extension = value[1]

                    if allowed_exts(extension) == True:
                        filename = value[0]
                        filename = sha256(str(filename).encode('utf-8'))

                        filename = str(filename.hexdigest()) + '.' + extension

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        payload['image'] = filename
                else:
                    payload["image"] = session["image"]
                
                payload["email"] = session["email"]
                payload["id"] = session["userid"]

                response = post_data_api("update-user", payload,auth=auth())
                if response == {}:
                    session["name"] = session["name"]
                    session["surname"] = session["surname"]
                    session["image"] = session["image"]
                    session["email"] = session["email"]
                    session["color"] = session["color"]
                else:
                    session["name"] = response["name"]
                    session["surname"] = response["surname"]
                    session["image"] = response["image"]
                    session["email"] = response["email"]
                    session["color"] = response["color"]
                return render_template("new_settings.html", notifications=notifications, notilist=notilist, noticount=noticount,noti_settings=noti_settings)
            else:
                data_to_api = { "settings": {}}

                for setting in [ "category_removed", "order_added", "order_removed", "category_added" ]:
                    payload = request.form.getlist(setting)

                    if len(payload) == 0:
                        mail = "0"
                        web = "0"
                    elif len(payload) == 1:
                        if "mail_1" in payload:
                            mail = "1"
                        elif "mail_0" in payload:
                            web = "0"
                        else:
                            mail = "0"
                        if "web_1" in payload:
                            web = "1"
                        elif "web_0" in payload:
                            web = "0"
                        else:
                            web = "0"
                    else:
                        for i in payload:
                            i = i.split("_")
                            i0 = i[0]
                            i1 = i[1]

                            if i0 == "mail":
                                mail = i1
                            elif i0 == "web":
                                web = i1

                    data_to_api["settings"][setting] = { "mail": mail, "web": web }


                return_data = post_data_api("settings",data_to_api,auth=auth())



                return redirect(url_for('settings'))
                ### USer Delete Part, disabled ... html ugly
                #if payload["mode"] == "regular":
                #    data = { "user_id": session["userid"], "budget_id": session["budget_id"], "force": False }
                #    return render_template("new_settings.html", notifications=notifications,  noticount=noticount)
                #elif payload["mode"] == "force":
                #    data = { "user_id": session["userid"], "budget_id": session["budget_id"], "force": True }
                #response = del_data_api("account", data)

                #if response == "DELuserOK":
                #    return redirect(url_for('logout'))
                #else:
                #    return render_template("new_settings.html", notifications=notifications, notilist=notilist, noticount=noticount)
               
    else:
        return redirect(url_for('login'))

# Budget Site, Budget verwaltung
@app.route('/budget', methods=["GET", "POST"])
def budget():
    if session:
        session["title"] = "budget"
        budget_id = session["budget_id"]
        user_id = session["userid"]
        noticount, notilist, notifications = get_notis()

        #connected_budgets = get_data_api("connected_budgets",data=budget_id,auth=auth())
        budget_member = get_data_api("budgetmember", data=budget_id,auth=auth())
        my_budgets = get_data_api("my_budgets",data=user_id,auth=auth())

        session["budgets"] = my_budgets
        if request.method == "GET":
            return render_template("budget_settings.html", budget_member=budget_member,my_budgets=my_budgets,notifications=notifications, notilist=notilist, noticount=noticount)

    else:
        return redirect(url_for('login'))

# Update Budget -> eventuell auf /budget umbauen
@app.route('/ubudget', methods=["POST"])
def ubudget():
    if session:
        if request.method == "POST":
            data = request.form.to_dict()

            response = post_data_api("ubudget", data=data,auth=auth())

            return redirect(url_for('budget'))

# Leave a Budget 
@app.route('/leave', methods=["GET"])
def leave():
    if session:
        budget_id = request.args['bid']

        data = { "budget_id": budget_id, "user_id": session["userid"], "force": "false"}

        response, text = post_data_api("leave",data,auth=auth())

        if not response:
            flash_message = {text: "danger"}
        else:
            flash_message = {text: "success"}

        flash(flash_message)

        my_budgets = get_data_api("my_budgets",data=session["userid"],auth=auth())
        session["budgets"] = my_budgets
        return redirect(url_for('budget'))
    else:
        return redirect(url_for('login'))

# Category Site Settings
@app.route('/category', methods=["GET", "POST"])
def category():
    if session:
        session["title"] = "category"
        budget_id = session["budget_id"]
        user_id = session["userid"]
        noticount, notilist, notifications = get_notis()

        categories = get_data_api("categorylist",data=budget_id,auth=auth())

        if request.method == "GET":
            return render_template("category.html", categories=categories,notifications=notifications, notilist=notilist, noticount=noticount)
            
        elif request.method == "POST":
            payload = request.form.to_dict()
            if "cat" in payload:
                payload["user_id"] = user_id
                payload["budget_id"] = budget_id
                response = post_data_api("categories", payload,auth=auth())
                if response == "True":
                    flash_message = {"Category added!": "success"}
                    categories = get_data_api("categorylist",data=budget_id,auth=auth())
                else:
                    flash_message = {"Error on creation": "danger"}

                flash(flash_message)

                return render_template("category.html", categories=categories,notifications=notifications, notilist=notilist, noticount=noticount)

            elif "newname" in payload:
                payload["budget_id"] = budget_id
                response = post_data_api("uCat", data=payload,auth=auth())

                if response:
                    flash_message = { "Category changed": "success"}
                else:
                    flash_message = { "Error at change": "danger"}

                flash(flash_message)

                return redirect(url_for('category'))
    else:
        return redirect(url_for('login'))

# category delete
@app.route('/delete')
def delete():
    if session:
        if request.args['name'] == "cat":
            id = request.args['id']

            data = { "cat_id": id, "budget_id": session["budget_id"] }
            return_value = del_data_api('categories',data,auth=auth())

            if return_value =="Entity deleted":
                flash_message = {"Category deleted": "success"}
            else:
                flash_message = {"Error at delete": "danger"}

            flash(flash_message)
            return category()
        elif request.args['name'] == "user":
            id = request.args['id']
            return_value = del_data_api('users',id)
            return budget()
        else:
            return "No such name"
    else:
        return redirect(url_for('login'))

# Delete Order by Timestamp -> nicht umbedingt perfekt wenn 2x gleichen Timestamp
@app.route('/delete-ts/<timestamp>')
def delete_ts(timestamp):
    if session:
        data = { "timestamp": timestamp, "budget_id": session["budget_id"] }
        return_value = del_data_api('orders',data,auth=auth())

        flash(return_value)

        return redirect(url_for('overview'))
    else:
        return redirect(url_for('login'))

# Confirm a Email Adresse per Shamail Variable -> Überedenken 
@app.route('/confirm')
def confirm():
    if session:
        mailhash = request.args.get("u")

        payload = { "hashed_mail": mailhash, "send": False}

        response = post_data_api("confirm", payload,auth=auth())

        if response == True:
            session["verified"] = "1"
            return render_template("confirm.html")
        else:
            return render_template("something502.html")
    else:
        return redirect(url_for('login'))


# Resend the email Verification Email
@app.route('/resend')
def resend():
    payload = { "send": True}

    response = post_data_api("confirm",payload,auth=auth())

    if response == True:
        return redirect(url_for('overview'))
    else: 
        return redirect(url_for('overview'))

# Updated das budget (color, name)
@app.route("/updateBudget",methods=["GET","POST"])
def updateBudget():
    if request.method == "POST":
        bid = request.form['id']
        session["budget_id"] = str(bid)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# Lest die Notifications -> wird per javascript executed
@app.route("/readNotis",methods=["GET","POST"])
def readNotis():
    if request.method == "POST":
        ids = request.form["ids"]

        ids = ids.split(",")
        if ids != ['']:

            payload = { "uid": str(session["userid"]), "notilist": ids }

            data = post_data_api("readNotis",payload,auth=auth())

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


# Zeigt alle bereits gelesenen Notifications  -> settings part für notifications
@app.route("/notifications",methods=["GET"])
def notifications():
    if session:
        session["title"] = "notifications"
        userid = session["userid"]
        noticount, notilist, notifications = get_notis()
        all_noticount, all_notilist, all_notifications = get_data_api("notis", data={"uid": userid, "show_all": True},auth=auth())
        return render_template("notifications.html", notifications=notifications, notilist=notilist, noticount=noticount,all_notifications=all_notifications)
    else:
        return redirect(url_for('login'))

@app.route('/pictures/<path:filename>', methods=["GET"])
def pictures(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
