from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory

from hashlib import sha256
import os
from app.views import app
from app.funcs import get_notis, auth, allowed_exts
from app.piglet_api import api
# Settings Site 
@app.route('/settings', methods=["GET", "POST"])
def settings():
    if session:
        session["title"] = "settings"
        pigapi = api(auth=session["authorization"])

        noticount, notilist, notifications = get_notis(pigapi)

        s, noti_settings = pigapi.get(url='user/settings')
        if request.method == "GET":
            pigapi.close()
            return render_template("new_settings.html", noti_settings=noti_settings, notifications=notifications, notilist=notilist, noticount=noticount)
            
        elif request.method == "POST":

            payload = request.form.to_dict()
            if "name" in payload:
                if request.files['image'].filename != '':
                    file = request.files['image']
                    filename = file.filename
                    value  = filename.split('.')
                    extension = value[1]

                    if allowed_exts(extension) == True:
                        filename = value[0]
                        filename = sha256(str(filename).encode('utf-8'))

                        filename = str(filename.hexdigest()) + '.' + extension

                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        payload['image'] = filename
                else:
                    payload["image"] = session["image"]
                
                payload["email"] = session["email"]
                payload["id"] = str(session["userid"])

                s, response = pigapi.put(url="user/update-user",data=payload)
                if response == {}:
                    session["name"] = session["name"]
                    session["surname"] = session["surname"]
                    session["image"] = session["image"]
                    session["email"] = session["email"]
                    session["color"] = session["color"]
                else:
                    session["name"] = response["name"]
                    session["surname"] = response["surname"]
                    session["image"] = response["image"]
                    session["email"] = response["email"]
                    session["color"] = response["color"]
                pigapi.close()
                return render_template("new_settings.html", notifications=notifications, notilist=notilist, noticount=noticount,noti_settings=noti_settings)
            else:

                data_to_api = { "settings": {}}

                for setting in [ "category_removed", "order_added", "order_removed", "category_added" ]:
                    payload = request.form.getlist(setting)

                    if len(payload) == 0:
                        mail = "0"
                        web = "0"
                    elif len(payload) == 1:
                        if "mail_1" in payload:
                            mail = "1"
                        elif "mail_0" in payload:
                            web = "0"
                        else:
                            mail = "0"
                        if "web_1" in payload:
                            web = "1"
                        elif "web_0" in payload:
                            web = "0"
                        else:
                            web = "0"
                    else:
                        for i in payload:
                            i = i.split("_")
                            i0 = i[0]
                            i1 = i[1]

                            if i0 == "mail":
                                mail = i1
                            elif i0 == "web":
                                web = i1

                    data_to_api["settings"][setting] = { "mail": mail, "web": web }
                
                s, return_data = pigapi.post(url="user/settings",data=data_to_api)
                pigapi.close()

                return redirect(url_for('settings'))
    else:
        pigapi.close()
        return redirect(url_for('login'))

@app.route('/pictures/<path:filename>', methods=["GET"])
def pictures(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
