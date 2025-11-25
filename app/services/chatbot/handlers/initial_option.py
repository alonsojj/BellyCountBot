# app/services/chatbot/handlers/initial_option.py
from typing import TYPE_CHECKING
from app.models.enums import ConversationState
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class InitialOptionHandler(StateHandler):
    """Handler para o estado onde o usuário escolhe a opção inicial."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        """Processa a escolha do usuário no menu inicial."""
        if user_message == "1":
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return service._enviar_para_atendente_humano(
                session, "Usuário novo, precisa de atenção."
            )
        elif user_message == "2":
            service._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
            return "Ok, vamos lá. Por favor, me informe seu CPF (11 números) ou CNPJ (14 números) para eu localizar seu cadastro.\n\n*(Digite 'Voltar' para o menu principal)*"
        elif user_message == "3":
            service._set_state(session, ConversationState.DOUBTS)
            return "Claro, por favor, descreva a sua dúvida e eu farei o meu melhor para responder.\n\n*(Digite 'Voltar' para o menu principal)*"
        else:
            # A chamada ao fallback da IA permanece no serviço principal por enquanto
            return await service._call_ia_fallback(session, user_message)
