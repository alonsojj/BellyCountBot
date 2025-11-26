from typing import TYPE_CHECKING
from app.models.enums import ConversationState
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class HumanAttendanceHandler(StateHandler):
    """Handler para gerenciar a conversa enquanto o usuário espera ou está em atendimento humano."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        return self.get_entry_message(service, session)

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        if session.state == ConversationState.HUMAN_ATTENDING:
            return (
                "Sua mensagem foi encaminhada ao especialista. Ele responderá em breve."
            )
        else:
            return "Você já está na fila para o atendimento humano. Por favor, aguarde mais um momento que um especialista logo falará com você.\n\n*(Se desejar recomeçar do zero, digite 'Voltar')*"

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        session.reset()
        return ConversationState.GREETING
