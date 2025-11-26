import logging
from typing import TYPE_CHECKING
from app.models.enums import ConversationState, AccountingService
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class IaConfirmationHandler(StateHandler):
    """Handler para o estado que aguarda a confirmação do usuário sobre a sugestão da IA."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        if user_message.lower() in ["sim", "s"]:
            session.client.service = AccountingService(session.ia_suggestion)
            logging.info(f"Usuário aceitou a sugestão da IA: {session.ia_suggestion}")

            if session.client.document_number:
                return await service._redirect_to_service_flow(
                    session, session.client.service.value
                )

            service._set_state(session, ConversationState.AGUARDANDO_CPF_CNPJ)
            new_handler = service.state_handlers[ConversationState.AGUARDANDO_CPF_CNPJ]
            return new_handler.get_entry_message(service, session)
        else:
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return (
                "Entendido. Desculpe pelo engano. Estou te encaminhando for um de nossos especialistas para entender melhor sua necessidade.\n\n"
                + service._enviar_para_atendente_humano(
                    session,
                    f"IA sugeriu '{session.ia_suggestion}', usuário recusou.",
                )
            )

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        return (
            f"Entendido. Pela sua descrição, parece que você precisa de: **{session.ia_suggestion}**.\n\n"
            "Isso está correto? (Sim/Não)\n\n"
            "*(Digite 'Voltar' para descrever novamente)*"
        )

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        return ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
