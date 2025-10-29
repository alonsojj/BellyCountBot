from app.services import (
    ChatbotService,
    WhatsAppService,
    AccessControlService,
    IaService,
)

ia_service_instance = IaService()
chatbot_service_instance = ChatbotService(ia_service_instance)
whatsapp_service_instance = WhatsAppService()
access_control_service_instance = AccessControlService()


def get_chatbot_service():
    return chatbot_service_instance


def get_whatsapp_service():
    return whatsapp_service_instance


def get_access_control_service():
    return access_control_service_instance
