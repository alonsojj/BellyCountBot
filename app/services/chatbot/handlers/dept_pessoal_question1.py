# app/services/chatbot/handlers/dept_pessoal_question1.py
from typing import TYPE_CHECKING
from app.models.enums import ConversationState
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class DeptPessoalQuestion1Handler(StateHandler):
    """Handler para a primeira pergunta do fluxo de Departamento Pessoal."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        contexto = (
            f"Solicitou: Departamento Pessoal. (Já possui funcionários: {user_message})"
        )
        service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        return service._enviar_para_atendente_humano(session, contexto)
