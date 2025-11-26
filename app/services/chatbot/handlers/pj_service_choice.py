from typing import TYPE_CHECKING
from app.models.enums import ConversationState, AccountingService
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class PjServiceChoiceHandler(StateHandler):
    """Handler para processar a escolha do menu de Serviços PJ."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.REGULARIZACAO_EMPRESA
            service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
            return service._enviar_para_atendente_humano(
                session, "Solicitou: Regularização de Empresa."
            )
        elif user_message == "2":
            session.client.service = AccountingService.DEPARTAMENTO_PESSOAL
            service._set_state(
                session, ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1
            )
            new_handler = service.state_handlers[
                ConversationState.SERVICO_DEPTO_PESSOAL_PERGUNTA_1
            ]
            return new_handler.get_entry_message(service, session)
        elif user_message == "3":
            session.client.service = AccountingService.ABERTURA_EMPRESA
            service._set_state(
                session, ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1
            )
            new_handler = service.state_handlers[
                ConversationState.SERVICO_ABERTURA_EMPRESA_PERGUNTA_1
            ]
            return new_handler.get_entry_message(service, session)
        elif user_message == "4":
            session.client.service = AccountingService.PLANEJAMENTO_PATRIMONIAL
            service._set_state(session, ConversationState.SERVICO_PLANEJAMENTO_MENU)
            new_handler = service.state_handlers[
                ConversationState.SERVICO_PLANEJAMENTO_MENU
            ]
            return new_handler.get_entry_message(service, session)
        elif user_message == "5":
            service._set_state(
                session, ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            )
            new_handler = service.state_handlers[
                ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            ]
            return new_handler.get_entry_message(service, session)
        else:
            ia_handler = service.state_handlers[
                ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            ]
            return await ia_handler.handle(service, session, user_message)

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        from app.services.chatbot.responses import menu_servicos_pj

        return menu_servicos_pj(session)

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        return ConversationState.AGUARDANDO_CPF_CNPJ
