# app/services/chatbot/handlers/pf_name.py
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
        return (
            f"Obrigado, {session.client.name}! Agora, por favor, escolha o serviço desejado:\n\n"
            + service._menu_servicos_pf(session)
        )
