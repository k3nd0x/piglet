from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory
from hashlib import sha256
import os
import json

from app.views import app
from app.funcs import get_notis, auth, allowed_exts

from app.piglet_api import api

# Neue Order hinzufügen /new-order
@app.route('/new-order', methods=["GET", "POST"])
def get_data():
    if session:
        session["title"] = "order"
        bid = session["budget_id"]
        pigapi = api(auth=session["authorization"])
        noticount, notilist, notifications = get_notis(pigapi)
        if request.method == "POST":
            data = request.form.to_dict()
            data["budget_id"] = bid

            s, categorylist = pigapi.get(url=f"category/{bid}")

            s, response = pigapi.post(url="order/new", data=data)

            if response == "Order added!":
                flash_message = {response: "danger"}
            else:
                flash_message = {response: "success"}

            flash(flash_message)
            pigapi.close()

            return redirect(url_for('get_data'))

        elif request.method == "GET":
            s, categorylist = pigapi.get(url=f"category/{bid}")
            pigapi.close()

            return render_template("new-order.html", categorylist=categorylist,notifications=notifications, notilist=notilist, noticount=noticount)
    else:
        return redirect(url_for('login'))

# Delete Order by Timestamp -> nicht umbedingt perfekt wenn 2x gleichen Timestamp
@app.route('/delete-ts/<timestamp>')
def delete_ts(timestamp):
    if session:
        budget_id = session["budget_id"]
        pigapi = api(auth=session["authorization"])
        s, return_value = pigapi.delete(url=f"order/{timestamp}?budget_id={budget_id}")

        flash(return_value)
        pigapi.close()

        return redirect(url_for('overview'))
    else:
        return redirect(url_for('login'))
