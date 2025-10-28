from ..models import Client


class ChatbotService:
    def __init__(self):
        self.user_sessions = {}

    def process_message(self, user_id, user_message):
        session = self.user_sessions.get(user_id)
        if not session:
            new_client = Client(user_id)
            self.user_sessions[user_id] = new_client
            response_message = "Bem vindo oq vc deseja"
        else:
            response_message = "vc ja me mandou msg antes"
        return response_message
