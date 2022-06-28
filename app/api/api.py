from fastapi import APIRouter

from app.api.endpoints import auth, devices, invoices, users, tasks

PREFIX = "/api/v1"
api_router = APIRouter()
api_router.include_router(auth.router, prefix=PREFIX + "/auth", tags=["auth"])
api_router.include_router(users.router, prefix=PREFIX + "/users", tags=["users"])
api_router.include_router(devices.router, prefix=PREFIX + "/devices", tags=["devices"])
api_router.include_router(
    invoices.router, prefix=PREFIX + "/invoices", tags=["invoices"]
)
api_router.include_router(tasks.router, prefix=PREFIX + "/tasks", tags=["tasks"])
