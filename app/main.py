from fastapi import FastAPI
from .api import webhook
from .api import access_control_router

app = FastAPI(title="BellyCountBot")

app.include_router(webhook.router)
app.include_router(access_control_router.router)
