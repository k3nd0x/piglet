from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory

from app.views import app
from app.funcs import get_notis, auth, allowed_exts

from app.piglet_api import api

# Category Site Settings
@app.route('/category', methods=["GET", "POST"])
def category():
    if session:
        session["title"] = "category"
        budget_id = session["budget_id"]
        user_id = session["userid"]
        url = "category/"
        pigapi = api(auth=session["authorization"])
        noticount, notilist, notifications = get_notis(pigapi)

        s, categories = pigapi.get(f"{url}{budget_id}")

        if not s:
            pigapi.close()
            return render_template("something502.html")

        if request.method == "GET":
            return render_template("category.html", categories=categories,notifications=notifications, notilist=notilist, noticount=noticount)
            
        elif request.method == "POST":
            payload = request.form.to_dict()
            if "cat" in payload:
                cat = payload["cat"]
                color = payload["color"]
                if "#" in color:
                    color = color.replace('#','')
                s,response = pigapi.post(f"{url}?catname={cat}&color={color}&budget_id={budget_id}")

                if response == "True":
                    flash_message = {"Category added!": "success"}
                    s, categories = pigapi.get(f"{url}{budget_id}")
                else:
                    flash_message = {"Error on creation": "danger"}

                pigapi.close()
                flash(flash_message)

                return render_template("category.html", categories=categories,notifications=notifications, notilist=notilist, noticount=noticount)

            elif "newname" in payload:
                name = payload["newname"]
                color = payload["color"]
                cat_id = payload["id"]

                if color == "" and name != "":
                    dataurl = f"{url}{cat_id}?budget_id={budget_id}&name={name}"
                elif color != "" and name == "":
                    if "#" in color:
                        color = color.replace('#','')
                    dataurl = f"{url}{cat_id}?budget_id={budget_id}&color={color}"
                elif color != "" and name != "":
                    if "#" in color:
                        color = color.replace('#','')
                    dataurl = f"{url}{cat_id}?budget_id={budget_id}&color={color}&name={name}"

                s, response = pigapi.put(dataurl)

                if response:
                    flash_message = { "Category changed": "success"}
                else:
                    flash_message = { "Error at change": "danger"}

                pigapi.close()
                flash(flash_message)
                return redirect(url_for('category'))
    else:
        return redirect(url_for('login'))

# category delete
@app.route('/delete')
def delete():
    if session:
        pigapi = api(auth=session["authorization"])
        if request.args['name'] == "cat":
            id = request.args['id']

            budget_id = session["budget_id"]

            s, return_value = pigapi.delete(f"category/{id}?budget_id={budget_id}")

            if return_value =="Entity deleted":
                flash_message = {"Category deleted": "success"}
            else:
                flash_message = {"Error at delete": "danger"}

            flash(flash_message)
            pigapi.close()
            return category()
        else:
            pigapi.close()
            return "No such name"
    else:
        return redirect(url_for('login'))