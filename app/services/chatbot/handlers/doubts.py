# app/services/chatbot/handlers/doubts.py
from typing import TYPE_CHECKING
from app.models.enums import ConversationState
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class DoubtsHandler(StateHandler):
    """
    Handler para quando o usuário tem uma dúvida.
    Chama a IA para responder e depois transiciona para o atendimento humano.
    """

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        # Reutiliza o método da IA do serviço principal
        ia_result = service.ia.handle_ai_request(session.chat_history, session.state)

        service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)

        if ia_result["status"] == "fail":
            return (
                ia_result["content"]
                + "\n\nPara garantir que você seja atendido, estou te encaminhando para um de nossos especialistas."
            )

        return (
            ia_result["content"]
            + "\n\nEspero ter ajudado! Se precisar de mais alguma coisa, um de nossos especialistas já foi acionado para falar com você."
        )
