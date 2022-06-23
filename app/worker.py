'''
celery worker
add worker here 
'''
import json

from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost")


@app.task(name="something meaningful")
def task_put_invoice(**args):
    pass