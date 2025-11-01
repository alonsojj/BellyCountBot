from app.services import (
    ChatbotService,
    WhatsAppService,
    AdminService,
    IaService,
)
from functools import lru_cache

@lru_cache
def get_ia_service():
    return IaService()

@lru_cache
def get_chatbot_service():
    return ChatbotService(get_ia_service())

@lru_cache
def get_whatsapp_service():
    return WhatsAppService()

@lru_cache
def get_admin_service():
    return AdminService()
