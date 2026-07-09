from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.routers import auth, items

app = FastAPI(title="API Testing Automation Framework - Sample Service", version="1.0.0")

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(items.router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}
