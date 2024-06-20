
from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response

from app.views import app
from app.funcs import get_notis
from app.piglet_api import api
import json
@app.route('/reports', methods=["GET", "POST"])
def reports():
    if session:
        pigapi = api(auth=session["authorization"])
        noticount, notilist, notifications = get_notis(pigapi)

        session["title"] = "report"
        budget_id = session["budget_id"]
        s, response = pigapi.get(url=f"reports/months?budget_id={budget_id}")
        months = response[0]
        years = response[1]

        if months == {'detail': 'Not Found'}:
            months = { "Not found": [ { "keine": "Einträge" } ] }

        if request.method == "GET" and session["month"] != "None" and session["year"] != "None":
            data = { "year": session["year"], "month": session["month"], "budget_id": str(session["budget_id"]) }

            s, reports = pigapi.get(url=f'reports/?year={session["year"]}&month={session["month"]}&budget_id={budget_id}')

            pre_year = session["preyear"]

            s,graphdata = pigapi.get(url=f"graph/?budget_id={budget_id}&month={session['month']}&year={session['year']}")
            s,comparedata = pigapi.get(url=f"graph/compare?budget_id={budget_id}&year1={session["year"]}&year2={pre_year}")
            s,avg_spend_per_cat = pigapi.get(url=f"graph/average?budget_id={budget_id}&year={session["year"]}&mode=category_spending")
            if reports == {'detail': 'Not found!'}:
                flash_message = {"No entries found for selected month": "danger" }
                flash(flash_message)
                return render_template("reports_get.html", years=years, months=months, notifications=notifications, noticount=noticount, notilist=notilist,comparedata=comparedata)

            reports = reports["users"]
            pigapi.close()

            return render_template("reports.html", months=months, years=years, graphdata=graphdata, reports=reports, notifications=notifications, noticount=noticount, notilist=notilist,comparedata=comparedata,avg_spend_per_cat=json.dumps(avg_spend_per_cat))

        elif request.method == "POST":
            data = request.values.get
            data = request.form.to_dict()

            if "." in data["month"]:
                data["month"] = data["month"].replace(".", "")

            month = data["month"]
            year = data["year"]
            session["month"] = month
            session["year"] = year

            pre_year = int(year) - 1

            session["preyear"] = pre_year

            s,graphdata = pigapi.get(url=f"graph/?budget_id={budget_id}&month={month}&year={year}")
            s,comparedata = pigapi.get(url=f"graph/compare?budget_id={budget_id}&year1={year}&year2={pre_year}")
            s,avg_spend_per_cat = pigapi.get(url=f"graph/average?budget_id={budget_id}&year={year}&mode=category_spending")

            s, reports = pigapi.get(url=f"reports/?year={year}&month={month}&budget_id={budget_id}")
            pigapi.close()

            if reports == {'detail': 'Not found!'}:
                flash_message = {"No entries in this month": "danger" }
                flash(flash_message)
                return render_template("reports_get.html", years=years, months=months, notifications=notifications, noticount=noticount, notilist=notilist)


            year = data["year"]
            month = reports["month"]
            reports = reports["users"]

            return render_template("reports.html", years=years, months=months, graphdata=graphdata, reports=reports, year=year,notifications=notifications, noticount=noticount, notilist=notilist,comparedata=comparedata,avg_spend_per_cat=json.dumps(avg_spend_per_cat))
        else:
            return render_template("reports_get.html", years=years, months=months,notifications=notifications, noticount=noticount, notilist=notilist)

    else:
        return redirect(url_for('login'))

