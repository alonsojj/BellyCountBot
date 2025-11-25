# app/services/chatbot/handlers/base.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService
    from app.models.user_session import UserSession


class StateHandler(ABC):
    """Classe base abstrata para todos os handlers de estado da conversa."""

    @abstractmethod
    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        """
        Processa a mensagem do usuário para um estado específico.

        Args:
            service: A instância do ChatbotService para acessar métodos compartilhados (_set_state, etc.).
            session: A sessão do usuário atual.
            user_message: A mensagem enviada pelo usuário.

        Returns:
            A mensagem de resposta para o usuário.
        """
        pass
