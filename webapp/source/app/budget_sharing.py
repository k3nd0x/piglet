from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response
from source.app import app
from werkzeug.utils import secure_filename


from .api_func import get_data_api,post_data_api
from .views import get_notis,auth



# FUnktion sendet eine Mail an den User der zum neuen Budget eingeladen wurde
@app.route('/sharewith', methods=["GET","POST"])
def share():
    if session:
        if request.method == "POST":
            #budget_id = session["budget_id"]
            _data = request.form.to_dict()

            data = { "shareto": _data["shareto"], "budget_id": _data["id"]}

            response = post_data_api("sharewith", data, auth=auth())

            if response["state"] == "Mail sent":
                flash_message = {"Email sent": "success"}
            else:
                string = "Email sending failed: URI {}".format(response["uri"])
                flash_message = {string: "danger"}

            flash(flash_message)

            return redirect(url_for('budget'))



@app.route('/link')
def link():
    session.clear()
    connect_id = request.args.get("u")

    session["share"] = connect_id

    return redirect(url_for('login'))

@app.route('/connect', methods=["GET","POST"])
def connect():
    if session:
        noticount, notilist, notifications = get_notis()
        if request.method == "GET":
            return render_template("connect.html",notifications=notifications, notilist=notilist, noticount=noticount)
        elif request.method == "POST":

            data = session["share"]

            response = post_data_api("connect", data, auth=auth())

            if response["detail"] == "OK":
                my_budgets = get_data_api("my_budgets",data=session["userid"],auth=auth())
                session["budgets"] = my_budgets
                flash_message = {"Join completed": "success"}
            elif response["detail"] == "Payment required":
                flash_message = {"Max budgets per user reached (currently 4)" : "danger"}
            elif response["detail"] == "Not found":
                flash_message = {"Link expired" : "danger"}
            else:
                flash_message = {"Failed to join" : "danger"}

            flash(flash_message)
            return redirect(url_for('connect'))
@app.route('/newbudget',methods=["GET", "POST"])
def newbudget():
    if session:
        noticount, notilist, notifications = get_notis()
        if request.method == "POST":
            form_data = request.form.to_dict()

            userid = session["userid"]
            name = form_data["budgetname"]
            currency = form_data["currency"]

            data = { "user_id": userid, "name": name, "currency": currency }

            response = post_data_api("newbudget", data,auth=auth())


        return redirect(url_for('budget'))


