# app/models/user_session.py
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
        # (Não limpamos os dados do client, como nome/documento)
