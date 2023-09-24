from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory
from datetime import date

from app.views import app
from app.funcs import get_notis
from app.piglet_api import api

@app.route('/futurespends', methods=["GET"])
def futurespends():
    if session:
        session["title"] = "futurespends"
        budget_id = session["budget_id"]
        data = { "budget_id": budget_id}
        if request.method == "GET":
            pigapi = api(auth=session["authorization"])
            noticount, notilist, notifications = get_notis(pigapi)
            session["title"] = "futurespends"

            s, apidata = pigapi.get(f"futurespends/?budget_id={budget_id}")

            orderlist = apidata["orders"]
            today = date.today()

            monthlist = apidata["monthlist"]
            valuelist = apidata["valuelist"]
            colorlist = apidata["colorlist"]

            s, categorylist = pigapi.get(f"category/{budget_id}")

            pigapi.close()

            return render_template("futurespends.html",orderlist=orderlist,notifications=notifications, notilist=notilist, noticount=noticount, monthlist=monthlist, valuelist=valuelist, colorlist=colorlist, categorylist=categorylist,today=today )
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/fdelete', methods=["GET","POST"])
def fdelete():
    if session:
        if request.args['name'] == "futurespends":
            pigapi = api(auth=session["authorization"])
            id = request.args['id']

            s, return_value = pigapi.delete(url=f"futurespends/{id}?budget_id={session['budget_id']}")

            if return_value =="Entity deleted":
                flash_message = {"Entity deleted": "danger"}
            else:
                flash_message = {"Error at delete": "danger"}

            flash(flash_message)
            pigapi.close()
            return futurespends()

@app.route('/new-futurespend', methods=["GET", "POST"])
def new_futurespend():
    if session:
        budget_id = session["budget_id"]
        userid = session["userid"]
        if request.method == "POST":
            pigapi = api(auth=session["authorization"])
            data = request.form.to_dict()
            data["userid"] = userid
            data["budget_id"] = budget_id

            s, response = pigapi.post(url="futurespends/new", data=data)
            if response == "Future spend added!":
                flash_message = {response: "danger"}
            else:
                flash_message = {response: "success"}

            flash(flash_message)

            pigapi.close()

            return redirect(url_for('futurespends'))

