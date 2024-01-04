from celery import Celery
from celery.schedules import crontab
from api.routes.mysql import sql 

from datetime import date

celery = Celery("taskforce")

celery.conf.broker_url = "redis://localhost:6379/1"
celery.conf.result_backend = "redis://localhost:6379/1"

celery.conf.result_expires=3600
celery.conf.task_serializer="json"
celery.conf.result_serializer="json"
celery.conf.accept_content=["json"]
celery.conf.broker_connection_retry_on_startup = True

@celery.task(name="futurespends")
def futurespends():
    today = date.today()
    mysql = sql()

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

celery.conf.beat_schedule = {
    "futurespends": {
        "task": "futurespends",
        "schedule": crontab(minute='0',hour='2')
    },
}