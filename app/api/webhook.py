from fastapi import APIRouter, Request, HTTPException
from pydantic import ValidationError
from ..models import WebhookPayload
from ..services import Messenger

router = APIRouter(prefix="/webhook", tags=["webhooks"])
_messenger = Messenger()
@router.post("/")
async def receive_webhook(request: Request):
    data = await request.json()
    try:
        payload = WebhookPayload(**data)
    except ValidationError as e:
        print("Erro", e)
        raise HTTPException(status_code=422, detail=e.errors())

    try:
        _messenger.send_text(payload.number, "Bem-vindo", instance_id=payload.instance)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"status": "ok"}
