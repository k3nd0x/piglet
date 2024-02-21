
from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response

import json

from app.views import app
from app.funcs import get_notis, auth, allowed_exts
from app.piglet_api import api


# Read notifications function - executed by js
@app.route("/readNotis",methods=["GET","POST"])
def readNotis():
    if session:
        pigapi = api(auth=session["authorization"])
        if request.method == "POST":
            ids = request.form["ids"]

            ids = ids.split(",")
            if ids != ['']:
                payload = { "uid": str(session["userid"]), "notilist": ids }

                s, data = pigapi.post('notifications/read',data=payload)
                pigapi.close()

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


# Shows all notifications 
@app.route("/notifications",methods=["GET"])
def notifications():
    if session:
        session["title"] = "notifications"
        userid = session["userid"]
        pigapi = api(auth=session["authorization"])
        noticount, notilist, notifications = get_notis(pigapi)

        s, notis = pigapi.get(f"notifications/?show_all=true")
        all_noticount = notis[0]
        all_notilist = notis[1]
        all_notifications = notis[2]
        pigapi.close()
        return render_template("notifications.html", notifications=notifications, notilist=notilist, noticount=noticount,all_notifications=all_notifications)
    else:
        return redirect(url_for('login'))