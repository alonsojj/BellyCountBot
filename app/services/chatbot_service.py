from ..models import Client


class ChatbotService:
    def __init__(self, ia):
        self.user_sessions = {}
        self.ia = ia

    def process_message(self, user_id, user_message):
        session = self.user_sessions.get(user_id)
        if not session:
            new_client = Client(user_id)
            self.user_sessions[user_id] = new_client
            response_message = f"Chat: {self.ia.get_response(user_message)}"
        else:
            response_message = f"Chat: {self.ia.get_response(user_message)}"
        return response_message
