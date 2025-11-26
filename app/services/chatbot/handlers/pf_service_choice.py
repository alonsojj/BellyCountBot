from typing import TYPE_CHECKING
from app.models.enums import ConversationState, AccountingService
from app.services.chatbot.handlers.base import StateHandler
from app.services.chatbot.responses import menu_servicos_pf

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class PfServiceChoiceHandler(StateHandler):
    """Handler para processar a escolha do menu de Serviços PF."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.IMPOSTO_RENDA_PF
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return service._enviar_para_atendente_humano(
                session, "Solicitou: Imposto de Renda Pessoa Física."
            )
        else:
            ia_handler = service.state_handlers[
                ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            ]
            return await ia_handler.handle(service, session, user_message)

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        return menu_servicos_pf(session)

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        if session.previous_state == ConversationState.AGUARDANDO_NOME_PF:
            return ConversationState.AGUARDANDO_NOME_PF
        return ConversationState.AGUARDANDO_CPF_CNPJ
