from fastapi import FastAPI

import backend.database.models  # noqa: F401
from backend.api.routers.user_router import router as user_router
from backend.api.routers.employee_router import router as employee_router
from backend.api.routers.file_router import router as file_router
from backend.api.routers.telegram_router import router as telegram_router
from backend.api.routers.webhook_router import router as webhook_router
from backend.api.routers.dialog_router import router as dialog_router
from backend.api.routers.lead_router import router as lead_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sentra API",
    )
    app.include_router(user_router)
    app.include_router(employee_router)
    app.include_router(file_router)
    app.include_router(telegram_router)
    app.include_router(webhook_router)
    app.include_router(dialog_router)
    app.include_router(lead_router)


    return app
