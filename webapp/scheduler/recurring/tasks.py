from ..celery_config import celery
from ..celery_config import sql

@celery.task(name="recurring")
def recurring_orders(schedule):
    try:
        mysql = sql()
    except Exception as e:
        return e
    try:
        query = f'''select o_id from pig_schedules where schedule="{schedule}"'''
        schedule_data = mysql.get(query)

        result = []

        for order in schedule_data:
            order_query = f'''select value,currency,user_id,category_id,budget_id,description from pig_orders where id={order["o_id"]}'''

            original_order = mysql.get(order_query)

            for i in original_order:
                value = i["value"]
                currency = i["currency"]
                user_id = i["user_id"]
                category_id = i["category_id"]
                budget_id = i["budget_id"]
                description = i["description"]
                
                query = f'''insert into pig_orders(value,currency,user_id,category_id,budget_id,description) VALUES ({value},"{currency}",{user_id},{category_id},{budget_id},"{description}")'''
                
                result.append(mysql.post(query))

        mysql.close()
        return result
    except Exception as e:

        mysql.close()
        return e