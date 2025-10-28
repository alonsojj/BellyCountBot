from app.services import (
    ChatbotService,
    WhatsAppService,
    AccessControlService,
)

chatbot_service_instance = ChatbotService()
whatsapp_service_instance = WhatsAppService()
access_control_service_instance = AccessControlService()


def get_chatbot_service():
    return chatbot_service_instance


def get_whatsapp_service():
    return whatsapp_service_instance


def get_access_control_service():
    return access_control_service_instance
