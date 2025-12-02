import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import ValidationError
from app.models import WebhookPayload, ConversationState
from app.services.chatbot import ChatbotService
from app.services import WhatsAppService, AdminService
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
    logging.debug(f"Webhook data received: {data}")
    try:
        payload = WebhookPayload(**data)
    except ValidationError as e:
        logging.error(f"ValidationError in webhook payload: {e}")
        raise HTTPException(status_code=422, detail=e.errors())
    print(acces_control_service.is_allowed(payload.user_id), payload.user_id)
    if payload.is_group or not acces_control_service.is_allowed(payload.user_id):
        return {"status": "ok"}

    current_state = chatbot_service.get_session_state(payload.user_id)

    if payload.is_me:
        if current_state in [
            ConversationState.ATENDIMENTO_HUMANO,
            ConversationState.HUMAN_ATTENDING,
        ]:
            chatbot_service.set_human_attending(payload.user_id)
        return {"status": "ok"}

    if payload.data.messageType != "conversation":
        response_text = "Desculpe, no momento só consigo processar mensagens de texto. Por favor, digite sua mensagem."
        whatsapp_service.send_text(payload.user_id, response_text, payload.instance)
        return {"status": "ok"}

    response_text = await chatbot_service.process_message(
        payload.user_id, payload.user_message, payload.instance
    )

    if response_text:
        whatsapp_service.send_text(payload.user_id, response_text, payload.instance)

    return {"status": "ok"}
