from app.services.chatbot import ChatbotService
from app.services import WhatsAppService, AdminService, IaService
from app.services.email_service import EmailService
from app.core.settings import get_settings

from functools import lru_cache


@lru_cache
def get_ia_service():
    return IaService()


@lru_cache
def get_email_service():
    return EmailService(get_settings())


@lru_cache
def get_chatbot_service():
    return ChatbotService(get_ia_service(), get_email_service())


@lru_cache
def get_whatsapp_service():
    return WhatsAppService()


@lru_cache
def get_admin_service():
    return AdminService()
