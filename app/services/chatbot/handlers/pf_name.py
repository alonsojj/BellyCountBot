from typing import TYPE_CHECKING
from app.models.enums import ConversationState
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class PfNameHandler(StateHandler):
    """Handler para aguardar o nome completo do cliente (Pessoa Física)."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        session.client.name = user_message.strip()

        if session.client.service:
            return await service._redirect_to_service_flow(
                session, session.client.service.value
            )

        service._set_state(session, ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF)
        new_handler = service.state_handlers[
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF
        ]
        return new_handler.get_entry_message(service, session)

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        return "CPF validado. Por favor, digite seu nome completo para prosseguirmos.\n\n*(Digite 'Voltar' para o menu principal)*"

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        return ConversationState.AGUARDANDO_CPF_CNPJ
