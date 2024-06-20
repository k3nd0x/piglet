from celery import Celery
from celery.schedules import crontab

from api.routes.mysql import sql 
import json
celery = Celery("taskforce")

celery.conf.broker_url = "redis://localhost:6379/1"
celery.conf.result_backend = "redis://localhost:6379/1"

celery.conf.result_expires=3600
celery.conf.task_serializer="json"
celery.conf.result_serializer="json"
celery.conf.accept_content=["json"]
celery.conf.broker_connection_retry_on_startup = True
celery.autodiscover_tasks(["scheduler.futurespends", "scheduler.recurring"])

celery_crontab_mapping = {
    "daily": crontab(minute=0, hour=7),
    "weekly": crontab(minute=0, hour=7, day_of_week=1),
    "monthly": crontab(minute=0, hour=7, day_of_month=1),
    "quarterly": crontab(minute=0, hour=7, day_of_month=1, month_of_year='1,4,7,10'),
    "halfyearly": crontab(minute=0, hour=7, day_of_month=1, month_of_year='1,7'),
    "yearly": crontab(minute=0, hour=7, day_of_month=1, month_of_year=1)
}


recurring_dict = {}
for key,value in celery_crontab_mapping.items():

    name = f"recurring_{key}"
    recurring_dict[name] = {
        "task": "recurring",
        "schedule": value,
        "args" : [ key ]
    }

celery.conf.beat_schedule = {
    "futurespends": {
        "task": "futurespends",
        "schedule": crontab(minute='*/2')
    },
}
celery.conf.beat_schedule.update(recurring_dict)