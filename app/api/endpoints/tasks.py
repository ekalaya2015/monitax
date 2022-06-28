from fastapi import APIRouter
from app.worker import add
import time

router = APIRouter()


@router.get("/hello")
async def hello():
    return {"message": "Hello World"}


@router.post("/add")
async def addition(
    x: int,
    y: int,
):
    task = add.delay(x, y)
    while not task.ready():
        time.sleep(1)

    return {"task_result": task.get()}
