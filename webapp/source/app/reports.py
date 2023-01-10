
from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response
from source.app import app

from .api_func import get_data_api,post_data_api
from .views import get_notis, auth

@app.route('/reports', methods=["GET", "POST"])
def reports():
    if session:
        noticount, notilist, notifications = get_notis()

        session["title"] = "report"
        budget_id = session["budget_id"]
        months = get_data_api('months',budget_id, auth=auth())
        if months == {'detail': 'Not Found'}:
            months = { "Not found": [ { "keine": "Einträge" } ] }

        if request.method == "GET" and session["month"] != "None" and session["year"] != "None":
            data = { "year": session["year"], "month": session["month"], "budget_id": str(session["budget_id"]) }

            #timestamps = get_data_api('timestamp', data)
            reports = get_data_api('reports', data, auth=auth())
            graphdata = get_data_api('graph_report',data, auth=auth())
            if reports == {'detail': 'Not found!'}:
                flash_message = {"Keine Einträge in diesem Monat": "danger" }
                flash(flash_message)
                return render_template("reports_get.html", months=months, notifications=notifications, noticount=noticount, notilist=notilist)

            year = session["year"]
            month = session["month"]
            reports = reports["users"]
            
            return render_template("reports.html", months=months, graphdata=graphdata, reports=reports, month=month, year=year,notifications=notifications, noticount=noticount, notilist=notilist)

        elif request.method == "POST":
            data = request.values.get
            data = request.form.to_dict()

            if "." in data["month"]:
                data["month"] = data["month"].replace(".", "")

            session["month"] = data["month"]
            session["year"] = data["year"]

            #timestamps = get_data_api('timestamp', data)
            graphdata = get_data_api('graph_report',data, auth=auth())
            reports = get_data_api('reports', data, auth=auth())

            if reports == {'detail': 'Not found!'}:
                flash_message = {"Keine Einträge in diesem Monat": "danger" }
                flash(flash_message)
                return render_template("reports_get.html", months=months, notifications=notifications, noticount=noticount, notilist=notilist)


            year = data["year"]
            month = reports["month"]
            reports = reports["users"]

            if "debt" in data:
                new_order = {}
                new_order["category"] = "Überweisung"
                new_order["value"] = data["debt"]
                new_order["user"] = data["user"]
                new_order["month"] = get_data_api('month-convert', data["month"], auth=auth())
                new_order["year"] = data["year"]
                debt = post_data_api("orders", new_order)

                #flash(debt)

                return render_template("reports_debt.html", months=months, graphdata=graphdata, reports=reports, month=month, debt=debt,year=year,notifications=notifications, noticount=noticount, notilist=notilist)
                #return return redirect(url_for('reports'))

            else:
                return render_template("reports.html", months=months, graphdata=graphdata, reports=reports, month=month, year=year,notifications=notifications, noticount=noticount, notilist=notilist)

        else:
            return render_template("reports_get.html", months=months,notifications=notifications, noticount=noticount, notilist=notilist)
            
    else:
        return redirect(url_for('login'))
