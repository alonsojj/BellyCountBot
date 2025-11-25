# app/services/chatbot/handlers/pf_service_choice.py
from typing import TYPE_CHECKING
from app.models.enums import ConversationState, AccountingService
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class PfServiceChoiceHandler(StateHandler):
    """Handler para processar a escolha do menu de Serviços PF."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.IMPOSTO_RENDA_PF
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return service._enviar_para_atendente_humano(
                session, "Solicitou: Imposto de Renda Pessoa Física."
            )
        else:
            return await service._call_ia_fallback(session, user_message)
