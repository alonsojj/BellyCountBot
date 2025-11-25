# app/services/chatbot/handlers/greeting.py
from typing import TYPE_CHECKING
from app.models.enums import ConversationState
from app.services.chatbot.handlers.base import StateHandler
from app.services.chatbot.responses import menu_inicial

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class GreetingHandler(StateHandler):
    """Handler para o estado inicial da conversa."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        """Define o próximo estado e retorna o menu inicial."""
        service._set_state(session, ConversationState.AGUARDANDO_OPCAO_INICIAL)
        return menu_inicial(session)
