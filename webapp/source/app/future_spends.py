from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory
from source.app import app
from werkzeug.utils import secure_filename
from hashlib import sha256
import os
import json

from .api_func import get_data_api, post_data_api, del_data_api
from .funcs import get_notis, auth

@app.route('/futurespends', methods=["GET"])
def futurespends():
    if session:
        session["title"] = "futurespends"
        budget_id = session["budget_id"]
        data = { "budget_id": budget_id}
        if request.method == "GET":
            noticount, notilist, notifications = get_notis()
            session["title"] = "futurespends"
            apidata = get_data_api("futurespends", data=data,auth=auth())
            orderlist = apidata["orders"]

            monthlist = apidata["monthlist"]
            valuelist = apidata["valuelist"]
            colorlist = apidata["colorlist"]

            categorylist = get_data_api("categorylist",data=budget_id,auth=auth())

            return render_template("futurespends.html",orderlist=orderlist,notifications=notifications, notilist=notilist, noticount=noticount, monthlist=monthlist, valuelist=valuelist, colorlist=colorlist, categorylist=categorylist )
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/fdelete', methods=["GET","POST"])
def fdelete():
    if session:
        if request.args['name'] == "futurespends":
            id = request.args['id']
            data = { "id": id, "budget_id": session["budget_id"] }
            return_value = del_data_api("futurespends",data,auth=auth())
            if return_value =="Entity deleted":
                flash_message = {"Entity deleted": "success"}
            else:
                flash_message = {"Error at delete": "danger"}

            flash(flash_message)
            return futurespends()

@app.route('/new-futurespend', methods=["GET", "POST"])
def new_futurespend():
    if session:
        budget_id = session["budget_id"]
        userid = session["userid"]
        if request.method == "POST":
            data = request.form.to_dict()
            data["userid"] = userid
            data["budget_id"] = budget_id

            response = post_data_api("futurespends", data,auth=auth())

            if response == "Future spend added!":
                flash_message = {response: "danger"}
            else:
                flash_message = {response: "success"}

            flash(flash_message)

            return redirect(url_for('futurespends'))
