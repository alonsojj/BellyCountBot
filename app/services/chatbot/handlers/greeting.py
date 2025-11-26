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
        """Ao receber qualquer mensagem no estado de saudação, simplesmente mostra o menu inicial."""
        return self.get_entry_message(service, session)

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        """Define o próximo estado e retorna o menu inicial."""
        service._set_state(session, ConversationState.AGUARDANDO_OPCAO_INICIAL)
        return menu_inicial(session)

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        """Voltar a partir do início não faz nada, apenas retorna ao mesmo estado."""
        return ConversationState.GREETING
