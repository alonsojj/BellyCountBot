from datetime import datetime
from app.models import Client
from app.models.enums import ConversationState


class UserSession:
    """
    Classe de modelo de dados para gerenciar o estado da sessão e os dados do cliente.
    """

    def __init__(self, user_id: str):
        self.client = Client(user_id=user_id)
        self.state = ConversationState.GREETING
        self.previous_state = ConversationState.GREETING
        self.chat_history = []
        self.ia_suggestion = None
        self.last_activity_time = datetime.now()
        self.whatsapp_instance = None

    def reset(self):
        """Reseta a sessão para o início."""
        self.state = ConversationState.GREETING
        self.previous_state = ConversationState.GREETING
        self.chat_history = []
        self.ia_suggestion = None

    def to_dict(self):
        """Converte a sessão do usuário para um dicionário serializável."""
        return {
            "user_id": self.client.user_id,
            "client": self.client.to_dict(),  # Usa o to_dict() do Client
            "state": self.state.value,
            "previous_state": self.previous_state.value,
            "chat_history": self.chat_history,
            "ia_suggestion": self.ia_suggestion,
            "last_activity_time": self.last_activity_time.isoformat(),
            "whatsapp_instance": self.whatsapp_instance,
        }
