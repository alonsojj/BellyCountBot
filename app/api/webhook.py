from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import ValidationError
from app.models import WebhookPayload
from app.services import WhatsAppService, ChatbotService, AdminService
from app.core.dependencies import (
    get_chatbot_service,
    get_whatsapp_service,
    get_admin_service,
)

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/")
async def receive_webhook(
    request: Request,
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service),
    acces_control_service: AdminService = Depends(get_admin_service),
):
    data = await request.json()
    print(data)
    try:
        payload = WebhookPayload(**data)
    except ValidationError as e:
        print("Erro", e)
        raise HTTPException(status_code=422, detail=e.errors())
    if (
        payload.is_me
        or payload.is_group
        or not acces_control_service.is_allowed(payload.user_id)
    ):
        return {"status": "ok"}
    if payload.data.messageType != "conversation":
        response_text = "Desculpe, no momento só consigo processar mensagens de texto. Por favor, digite sua mensagem."
        whatsapp_service.send_text(payload.user_id, response_text, payload.instance)
        return {"status": "ok"}
    response_text = chatbot_service.process_message(
        payload.user_id, payload.user_message
    )

    if response_text:
        whatsapp_service.send_text(payload.user_id, response_text, payload.instance)

    return {"status": "ok"}
