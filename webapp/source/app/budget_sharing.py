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

            if response["detail"] == "OK":
                flash_message = {"Email wurde versendet": "success"}
            else:
                flash_message = {"Fehler beim einladen": "danger"}

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
                flash_message = {"Beitritt abgeschlossen": "success"}
            elif response["detail"] == "Payment required":
                flash_message = {"Maximale Anzahl ausgereizt" : "danger"}
            elif response["detail"] == "Not found":
                flash_message = {"Der Link ist abgelaufen" : "danger"}
            else:
                flash_message = {"Fehler beim joinen" : "danger"}

            flash(flash_message)
            return redirect(url_for('connect'))






