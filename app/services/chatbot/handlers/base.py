# app/services/chatbot/handlers/base.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from app.models.enums import ConversationState

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService
    from app.models.enums import ConversationState
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
            service: A instância do ChatbotService para acessar métodos compartilhados.
            session: A sessão do usuário atual.
            user_message: A mensagem enviada pelo usuário.

        Returns:
            A mensagem de resposta para o usuário.
        """
        pass

    @abstractmethod
    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        """
        Retorna a mensagem que o usuário vê ao entrar neste estado.

        Args:
            service: A instância do ChatbotService.
            session: A sessão do usuário atual.

        Returns:
            A mensagem de boas-vindas/instrução para este estado.
        """
        pass

    @abstractmethod
    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        """
        Determina para qual estado retornar a partir do estado atual.

        Args:
            service: A instância do ChatbotService.
            session: A sessão do usuário atual.

        Returns:
            O estado para o qual a conversa deve reverter.
        """
        pass
