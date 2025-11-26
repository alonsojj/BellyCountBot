from typing import TYPE_CHECKING
from app.models.enums import ConversationState, AccountingService
from app.services.chatbot.handlers.base import StateHandler

if TYPE_CHECKING:
    from app.services.chatbot.chatbot_service import ChatbotService, UserSession


class PlanejamentoMenuHandler(StateHandler):
    """Handler para o menu de serviços de Planejamento."""

    async def handle(
        self, service: "ChatbotService", session: "UserSession", user_message: str
    ) -> str:
        if user_message == "1":
            session.client.service = AccountingService.PLANEJAMENTO_REDUZIR_CARGA
            contexto = "Solicitou: Planejamento (Reduzir carga tributária)"
        elif user_message == "2":
            session.client.service = AccountingService.PLANEJAMENTO_REESTRUTURAR_REGIME
            contexto = "Solicitou: Planejamento (Reestruturar regime)"
        elif user_message == "3":
            session.client.service = (
                AccountingService.PLANEJAMENTO_CONSULTORIA_PREVENTIVA
            )
            contexto = "Solicitou: Planejamento (Consultoria preventiva)"
        elif user_message == "4":
            session.client.service = AccountingService.PLANEJAMENTO_REVISAR_TRIBUTOS
            contexto = "Solicitou: Planejamento (Revisar tributos pagos)"
        else:
            ia_handler = service.state_handlers[
                ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION
            ]
            return await ia_handler.handle(service, session, user_message)

        service._set_state(session, ConversationState.ATENDIMENTO_HUMANO)
        return service._enviar_para_atendente_humano(session, contexto)

    def get_entry_message(
        self, service: "ChatbotService", session: "UserSession"
    ) -> str:
        from app.services.chatbot.responses import menu_planejamento

        return menu_planejamento(session)

    def handle_back(
        self, service: "ChatbotService", session: "UserSession"
    ) -> ConversationState:
        return ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ
