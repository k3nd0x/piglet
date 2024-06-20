from ..celery_config import celery
from ..celery_config import sql
from datetime import date

@celery.task(name="futurespends")
def futurespends():

    try:
        mysql = sql()
    except Exception as e:
        return e
    try:
        today = date.today()

        query = '''select (select id from registered_user where id=user_id) as user, (select id from pig_category where id=category_id) as category, value, currency, id, DATE_FORMAT(timestamp, '%Y-%m-%d') as timestamp,description,budget_id FROM pig_futurespends order by timestamp DESC'''

        response = mysql.get(query)

        return_list = []

        for i in response:
            if str(i["timestamp"]) == str(today):
                query = '''insert into new_orders(value,currency,user_id,category_id,budget_id,description) VALUES ({},"{}",{},{},{},"{}")'''.format(i["value"],i["currency"],i["user"],i["category"],i["budget_id"],i["description"])

                remove_query = f'''delete from pig_futurespends where id={i["id"]}'''
                mysql.post(remove_query)
                response = mysql.post(query)

                return_list.append(response)
        mysql.close()
        return return_list
    except Exception as e:
        mysql.close
        return e

