# app/services/chatbot/handlers/human_attendance.py
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
        # A lógica de "voltar" reseta a sessão se o usuário estiver em atendimento.
        # A mensagem principal do webhook já não repassa a mensagem para o bot se
        # o estado for HUMAN_ATTENDING, então esta lógica é mais para o estado
        # ATENDIMENTO_HUMANO (a fila).

        if session.state == ConversationState.HUMAN_ATTENDING:
            # Esta resposta não deve ser enviada na prática, pois o webhook não chamaria o bot.
            # Mas, por segurança, mantemos uma resposta.
            return (
                "Sua mensagem foi encaminhada ao especialista. Ele responderá em breve."
            )
        else:
            # O usuário está no estado ATENDIMENTO_HUMANO, ou seja, na fila.
            return "Você já está na fila para o atendimento humano. Por favor, aguarde mais um momento que um especialista logo falará com você.\n\n*(Se desejar recomeçar do zero, digite 'Voltar')*"
