from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response
from werkzeug.utils import secure_filename


from app.views import app
from app.funcs import get_notis, auth, allowed_exts
from app.piglet_api import api

import json


# Function sends a notification to the destination user
@app.route('/sharewith', methods=["GET","POST"])
def share():
    if session:
        pigapi = api(auth=session["authorization"])
        if request.method == "POST":
            _data = request.form.to_dict()

            budget_id = _data["id"]
            shareto = _data["shareto"]

            try:
                s, response = pigapi.post(url=f"share/newshare?budget_id={budget_id}&shareto={shareto}")

                if s:
                    flash_message = {response: "success"}
                else:
                    string = "Budget sharing failed"
                    flash_message = {string: "danger"}
            except:
                string = "Budget sharing failed"
                flash_message = {string: "danger"}


            flash(flash_message)
            pigapi.close()

            return redirect(url_for('budget'))

# Adds a new budget to the user
@app.route('/newbudget',methods=["GET", "POST"])
def newbudget():
    if session:
        pigapi = api(auth=session["authorization"])
        noticount, notilist, notifications = get_notis(pigapi)

        if request.method == "POST":
            form_data = request.form.to_dict()

            userid = session["userid"]
            name = form_data["budgetname"]
            currency = form_data["currency"]

            data = { "user_id": userid, "name": name, "currency": currency }

            s, response = pigapi.post(url=f"budget/add?name={name}&currency={currency}", data=data)

        pigapi.close()

        return redirect(url_for('budget'))


# Budget Site, Budget verwaltung
@app.route('/budget', methods=["GET", "POST"])
def budget():
    if session:
        pigapi = api(auth=session["authorization"])
        session["title"] = "budget"
        budget_id = session["budget_id"]
        user_id = session["userid"]
        noticount, notilist, notifications = get_notis(pigapi)

        s, my_budgets = pigapi.get(url="budget/")
        s, users = pigapi.get(url=f'share/availusers/{budget_id}')

        session["budgets"] = my_budgets
        if request.method == "GET":
            return render_template("budget_settings.html", my_budgets=my_budgets,availusers=users,notifications=notifications, notilist=notilist, noticount=noticount)

    else:
        return redirect(url_for('login'))

# Change budget color/name/currency
@app.route('/ubudget', methods=["POST"])
def ubudget():
    if session:
        pigapi = api(auth=session["authorization"])
        if request.method == "POST":
            data = request.form.to_dict()
            budget_id = data["id"]

            name = data["newname"]
            currency = data["newcurrency"]
            s, response = pigapi.put(url=f'budget/{budget_id}?name={name}&currency={currency}')

            pigapi.close()

            return redirect(url_for('budget'))

# Leave a Budget 
@app.route('/leave', methods=["GET"])
def leave():
    if session:
        pigapi = api(auth=session["authorization"])
        budget_id = request.args['bid']

        s,response = pigapi.post(url=f'budget/leave/{budget_id}?force=false')

        text = response[1]
        response = response[0]

        if not response:
            flash_message = {text: "danger"}
        else:
            flash_message = {text: "success"}

        flash(flash_message)

        s, my_budgets = pigapi.get(url=f'budget/')
        pigapi.close()

        session["budgets"] = my_budgets
        return redirect(url_for('budget'))
    else:
        return redirect(url_for('login'))

# Change the current active budget over navbar / ajax
@app.route("/updateBudget",methods=["GET","POST"])
def updateBudget():
    if request.method == "POST":
        bid = request.form['id']
        session["budget_id"] = str(bid)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}



@app.route("/joinBudget", methods=["GET","POST"])
def joinBudget():
    if session:
        bid = request.args['id']
        join = "true"

        pigapi = api(auth=session["authorization"])

        s, response = pigapi.post(url=f'share/updatejoin?budget_id={bid}&join={join}')

        pigapi.close()

        if s:
            string = "You joined a budget"
            flash_message = {string: "success"}
        else:
            string = "Budget joining failed"
            flash_message = {string: "danger"}
        
        flash(flash_message)
        return redirect(url_for('budget'))
    else:
        return redirect(url_for('login'))


@app.route("/discardBudget", methods=["GET","POST"])
def discardBudget():
    if session:
        bid = request.args['id']
        join = "false"

        pigapi = api(auth=session["authorization"])

        s, response = pigapi.post(url=f'share/updatejoin?budget_id={bid}&join={join}')

        pigapi.close()

        if s:
            string = "You discarded a budget join request"
            flash_message = {string: "success"}
        else:
            string = "Discarding join request failed"
            flash_message = {string: "danger"}
        
        flash(flash_message)
        return redirect(url_for('budget'))
    else:
        return redirect(url_for('login'))