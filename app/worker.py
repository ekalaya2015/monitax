"""
celery worker
add worker here 
"""

from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost")


@app.task(name="addition")
def add(x, y):
    """
    add two numbers. Just a sample task.
    """
    return x + y
