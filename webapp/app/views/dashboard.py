from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory

from app.views import app
from app.funcs import get_notis, auth, allowed_exts
from app.piglet_api import api
# Default Index
@app.route('/', methods=["GET"])
def overview():
    if session:
        userid = session["userid"]
        budget_id = session["budget_id"]

        data = { "budget_id": budget_id}
        if request.method == "GET":
            pigapi = api(auth=session["authorization"])
            session["title"] = "dashboard"
            s, orderlist = pigapi.get(url=f"order/?budget_id={budget_id}")
            s, graphdata = pigapi.get(f"graph/?budget_id={budget_id}")

            noticount, notilist, notifications = get_notis(pigapi)
            pigapi.close()

            return render_template("index.html", orderlist=orderlist,graphdata=graphdata,notifications=notifications, notilist=notilist, noticount=noticount )
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
