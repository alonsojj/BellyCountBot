from fastapi import FastAPI
from .api import webhook
from .api import admin


app = FastAPI(title="BellyCountBot")

app.include_router(webhook.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
