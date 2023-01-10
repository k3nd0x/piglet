from flask import Flask, render_template, flash, request, session, url_for, redirect, Markup, make_response
from passlib.hash import sha256_crypt as sha256
import hashlib
import uuid
from datetime import datetime, timedelta
from source.app import app

from flask import jsonify

from .api_func import post_data_api,get_data_api,get_token


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.values.get
        data = request.form.to_dict()

        if data["password1"] != data["password2"]:
            flash_message = { 'Passwörter stimmen nicht überein': "danger" }
            flash(flash_message)
            return render_template("register.html")
        
        salt = uuid.uuid4().hex

        password = hashlib.sha256(salt.encode() + data["password1"].encode()).hexdigest() + ':' + salt
        email = data["email"]

        create_dict = {}
        create_dict["email"] = email
        create_dict["password"] = password
        
        response = post_data_api("register",create_dict)

        if response == {'detail': 'User already exists'}:
            flash_message = { Markup('User {email} existiert bereits <a href="/login?email={email}">Hier einloggen</a>'.format(email=email)): "danger" }
            flash(flash_message)
            return render_template("register.html")
        else:
            return redirect(url_for('login'))
    elif request.method == "GET":
        return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form.to_dict()
        responsare = get_token(data)

        if responsare == {'detail': 'Bad Request'}:
            flash_message = { "Falsche Email oder Passwort": "danger"}
            flash(flash_message)
            return render_template("login.html")
        elif responsare == {'detail': 'Not found'}:
            flash_message = { Markup("User {} nicht gefunden <a href='/register'>Hier registrieren</a>".format(data["email"])): "danger"}
            flash(flash_message)
            return render_template("login.html")

        else:
            email = data["email"]
            session["authorization"] = responsare["access_token"]
            response = get_data_api("login", email,auth=responsare["access_token"])

            session["userid"] = response["id"]
            my_budgets = get_data_api("my_budgets",data=response["id"],auth=responsare["access_token"])


            session["email"] = response['email']
            session["image"] = response["image"]
            session["color"] = response["color"]
            session["month"] = "None"
            session["year"] = "None"
            session["budget_id"] = str(response["budget_id"])
            session["budgets"] = my_budgets
            session["verified"] = response["verified"]
            session["title"] = "blank"
            
            x = "test"
            session["test"] = x
            print(session)


            if response["name"] != None:
                session["name"] = response["name"]
            else:
                session["name"] = email

            if response["surname"] != None:
                session["surname"] = response["surname"]
            else:
                session["surname"] = email


            try:
                if session["share"]:
                    return redirect(url_for("connect"))
            except KeyError:
                return redirect(url_for('overview'))

            return redirect(url_for('overview'))

    else:
        return render_template("login.html")



@app.route('/passwordlost', methods=['GET', 'POST'])
def passwordlost():
    if request.method == "GET":
        return render_template("passwordlost.html")
    elif request.method == "POST":
        data = request.form.to_dict()
        data["tmphash"] = ""
        response = post_data_api("forgot",data)

        if response[0] == True:
            return render_template("passwordlostsuccess.html")
        elif response[0] == False:
            if response[1] == "alreadyProvided":
                flash_message = { "Passwort zurücksetzten wurde innerhalb der letzten 15 Minuten bereits angefordert": "danger"}
            elif response[1] == "UserNotAvailable":
                flash_message = { "User nicht bekannt": "danger"}

            flash(flash_message)

            return render_template("passwordlost.html")


        
@app.route('/reset', methods=['GET'])
def passwordreset():
    userhash = request.args.get("u")
    session["tmp"] = userhash
    if request.method == "GET":
        data = { "tmphash": userhash, "email": "" }

        response = post_data_api("forgot", data)

        if response == True:
            return redirect(url_for("newpw"))
        else:
            flash_message = { "Link expired": "danger"}
            flash(flash_message)
            return render_template("resetpassword.html")

@app.route('/newpw', methods=['GET', 'POST'])
def newpw():
    if session:
        if request.method == "GET":
            return render_template("resetpassword.html")
        elif request.method == "POST":
            data = request.form.to_dict()
            if data["password1"] != data["password2"]:
                flash_message = { 'Passwörter stimmen nicht überein': "danger" }
                flash(flash_message)
                return render_template("resetpassword.html")
            else:
                tmphash = session["tmp"]
                salt = uuid.uuid4().hex
                password = hashlib.sha256(salt.encode() + data["password1"].encode()).hexdigest() + ':' + salt

                data = { "tmphash": tmphash, "passwordhash": password }

                response = post_data_api("reset", data)

                session.clear()
                if response:
                    return redirect(url_for('login'))
                else:
                    flash_message = { "Reset failed try again later": "danger"}
                    flash(flash_message)

                    return render_template("resetpassword.html")
    else: 
        return redirect(url_for('login'))


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))
