from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import ValidationError
from app.models import WebhookPayload
from app.services import WhatsAppService, ChatbotService, AccessControlService
from app.dependencies import (
    get_chatbot_service,
    get_whatsapp_service,
    get_access_control_service,
)

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/")
async def receive_webhook(
    request: Request,
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service),
    acces_control_service: AccessControlService = Depends(get_access_control_service),
):
    data = await request.json()
    print(data)
    try:
        payload = WebhookPayload(**data)
    except ValidationError as e:
        print("Erro", e)
        raise HTTPException(status_code=422, detail=e.errors())
    if not (acces_control_service.is_allowed(payload.user_id) and not payload.is_me):
        return {"status": "ok"}

    response_text = chatbot_service.process_message(
        payload.user_id, payload.user_message
    )

    if response_text:
        whatsapp_service.send_text(payload.user_id, response_text, payload.instance)

    return {"status": "ok"}
