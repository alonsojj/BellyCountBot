from typing import TYPE_CHECKING
from app.models.enums import ConversationState
from app.services.chatbot.handlers.base import StateHandler
from app.services.chatbot.responses import menu_inicial

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class InitialOptionHandler(StateHandler):
    """Handler para o estado onde o usuário escolhe a opção inicial."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        """Processa a escolha do usuário no menu inicial."""
        if user_message == "1":
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            new_handler = service.state_handlers[ConversationState.ATENDIMENTO_HUMANO]
            return new_handler.get_entry_message(service, session)
        elif user_message == "2":
            service._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
            new_handler = service.state_handlers[ConversationState.AGUARDANDO_CPF_CNPJ]
            return new_handler.get_entry_message(service, session)
        elif user_message == "3":
            service._set_state(session, ConversationState.DOUBTS)
            new_handler = service.state_handlers[ConversationState.DOUBTS]
            return new_handler.get_entry_message(service, session)
        else:
            ia_handler = service.state_handlers[
                ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            ]
            return await ia_handler.handle(service, session, user_message)

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        return menu_inicial(session)

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        return ConversationState.GREETING
