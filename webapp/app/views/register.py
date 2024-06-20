from flask import render_template, flash, request, session, url_for, redirect
from passlib.hash import sha256_crypt as sha256
import hashlib
import uuid

from app.views import app
from app.funcs import get_notis, auth, allowed_exts
from app.piglet_api import api

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.values.get
        data = request.form.to_dict()

        if data["password1"] != data["password2"]:
            flash_message = { 'Passwords are not the same': "danger" }
            flash(flash_message)
            return render_template("register.html")
        
        salt = uuid.uuid4().hex

        password = hashlib.sha256(salt.encode() + data["password1"].encode()).hexdigest() + ':' + salt
        email = data["email"]

        create_dict = {}
        create_dict["email"] = email
        create_dict["password"] = password

        pigapi = api()

        s, response = pigapi.post(url="user/register_user",data=create_dict)
        pigapi.close()
        if s:
            if response == {'detail': 'User already exists'}:
                flash_message = { 'User {email} is already existing'.format(email=email): "danger" }
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

        #responsare = get_token(data)
        pigapi = api()
        code,responsare = pigapi.get_token(payload=data)

        if responsare == {'detail': 'Bad Request'}:
            flash_message = { "Wrong Email or Password": "danger"}
            flash(flash_message)
            return render_template("login.html")
        elif responsare == {'detail': 'Not found'}:
            flash_message = { "User {} not found".format(data["email"]): "danger"}
            flash(flash_message)
            return render_template("login.html")
        elif code != 200:
            flash_message = { "Something went wrong - try again later": "danger"}
            flash(flash_message)
            return render_template("login.html")
        else:
            session["authorization"] = responsare["access_token"]
            pigapi = api(auth=session["authorization"])
            try:
                email = data["email"]
                s, response = pigapi.get(url="user/login-user",data=email)

                if s:
                    session["email"] = response['email']
                    session["image"] = response["image"]
                    session["color"] = response["color"]
                    session["budget_id"] = str(response["budget_id"])
                    session["verified"] = response["verified"]
                    session["userid"] = response["id"]
                    if response["name"]:
                        session["name"] = response["name"]
                    else:
                        session["name"] = email
                    if response["surname"]:
                        session["surname"] = response["surname"]
                    else:
                        session["surname"] = email
                s, my_budgets = pigapi.get(url="budget/")
                if s:
                    session["month"] = "None"
                    session["year"] = "None"
                    session["budgets"] = my_budgets
                    session["title"] = "blank"
                pigapi.close()
            except:
                pigapi.close()
                return render_template("waittillstartup.html")
            try:
                pigapi.close()
                if session["share"]:
                    return redirect(url_for("connect"))
            except KeyError:
                pigapi.close()
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
        email = data["email"]
        pigapi = api()

        s, response = pigapi.post(url=f'user/forgot-request?email={email}')

        pigapi.close()

        if response[0] == True:
            return render_template("passwordlostsuccess.html")
        elif response[0] == False:
            if response[1] == "alreadyProvided":
                flash_message = { "Reset password has already been requested within the last 15 Minutes": "danger"}
            elif response[1] == "UserNotAvailable":
                flash_message = { "User not known": "danger"}

            flash(flash_message)

            return render_template("passwordlost.html")


        
@app.route('/reset', methods=['GET'])
def passwordreset():
    userhash = request.args.get("u")
    session["tmp"] = userhash
    if request.method == "GET":

        pigapi = api()

        s, response = pigapi.post(url=f'user/forgot-request?tmphash={userhash}')
        pigapi.close()

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
                flash_message = { 'Passwords are not the same': "danger" }
                flash(flash_message)
                return render_template("resetpassword.html")
            else:
                tmphash = session["tmp"]
                salt = uuid.uuid4().hex
                password = hashlib.sha256(salt.encode() + data["password1"].encode()).hexdigest() + ':' + salt

                pigapi = api()
                s, response = pigapi.put(url=f'user/update-pw?passwordhash={password}&tmphash={tmphash}')
                pigapi.close()

                session.clear()
                if response:
                    return redirect(url_for('login'))
                else:
                    flash_message = { "Reset failed try again later": "danger"}
                    flash(flash_message)

                    return render_template("resetpassword.html")
    else: 
        return redirect(url_for('login'))


# Confirm a Email Adresse per Shamail Variable -> Überedenken 
@app.route('/confirm')
def confirm():
    if session:
        mailhash = request.args.get("u")
        send = False

        pigapi = api(auth=session["authorization"])
        s, response = pigapi.put(f"user/confirm?hashed_mail={mailhash}&send={send}")
        pigapi.close()

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
    send = True

    pigapi = api(auth=session["authorization"])
    s, response = pigapi.put(f"user/confirm?send={send}")
    pigapi.close()

    if response == True:
        return redirect(url_for('overview'))
    else: 
        return redirect(url_for('overview'))

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))
