from fastapi import APIRouter
from app.core import config
from app.api.endpoints import auth, devices, invoices, users, tasks

api_router = APIRouter()
api_router.include_router(
    auth.router, prefix=config.settings.API_PREFIX + "/auth", tags=["auth"]
)
api_router.include_router(
    users.router, prefix=config.settings.API_PREFIX + "/users", tags=["users"]
)
api_router.include_router(
    devices.router, prefix=config.settings.API_PREFIX + "/devices", tags=["devices"]
)
api_router.include_router(
    invoices.router, prefix=config.settings.API_PREFIX + "/invoices", tags=["invoices"]
)
api_router.include_router(
    tasks.router, prefix=config.settings.API_PREFIX + "/tasks", tags=["tasks"]
)
