from fastapi import FastAPI
from .api import webhook

app = FastAPI(title="BellyCountBot")

app.include_router(webhook.router)
